from __future__ import annotations

import logging
from datetime import datetime as dt
from functools import partial
from pathlib import Path
from sys import stderr
from typing import Callable

import dateparser
import frontmatter
import markdown
import pandas as pd
from staticjinja import Site

from ..auditing import AuditBuilder, Auditer
from ..ns_util import cyl_path, ns, ns_path

__all__ = ["cyl", "standup"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pymd_extensions = (
    "fenced_code codehilite sane_lists def_list admonition toc markdown_katex".split()
)
extension_configs = {
    "markdown_katex": {"no_inline_svg": True, "insert_fonts_css": False},
}
markdowner = markdown.Markdown(
    output_format="html5",
    extensions=pymd_extensions,
    extension_configs=extension_configs,
)

OUT_DIRNAME = "site"
TEMPLATE_DIRNAME = "src"
POST_DIRNAME = "posts"

global GLOBAL_CTX_COUNT
GLOBAL_CTX_COUNT = {}


def log(msg, use_logger=False):
    if use_logger:
        logger.info(msg)
    else:
        print(msg, file=stderr)


def cyl(
    domains_list: list[str] | None = None,
    *,
    incremental: bool = False,
    verbose: bool = True,
):
    standup(
        domains_list=domains_list,
        incremental=incremental,
        internal=False,
        verbose=verbose,
    )


def standup(
    domains_list: list[str] | None = None,
    *,
    internal: bool = True,
    incremental: bool = False,
    verbose: bool = True,
):
    domains_list = domains_list or [*ns]
    for domain in domains_list:
        ns_in_p = ns_path / domain
        if not (ns_in_p.exists() and ns_in_p.is_dir()):
            raise ValueError(f"{ns_in_p} not found")
        # ns_in_p for input and ns_out_p for output (not necessarily same)
        ns_out_p = (ns_path if internal else cyl_path) / domain
        site_dir = ns_out_p / (OUT_DIRNAME if internal else ".")
        template_dir = ns_in_p / TEMPLATE_DIRNAME
        if template_dir.exists():
            if incremental:
                audit_p = ns_out_p.parent / f"{domain}.tsv"
                if not audit_p.exists():
                    audit_p.touch()
                audit_builder = AuditBuilder.from_path(active=True, path=audit_p)
            else:
                audit_builder = AuditBuilder(active=False, auditer=None)
            post_dir = template_dir / POST_DIRNAME
            extra_ctxs = []
            if post_dir.exists():
                post_dir_sans_drafts = [
                    a for a in post_dir.iterdir() if a.name != "drafts"
                ]
                for a in post_dir_sans_drafts:
                    log(f"POST: {a}")
                post_leaf_dir = Path(POST_DIRNAME)
                post_ctxs = [
                    (str(post_leaf_dir / a.name), article) for a in post_dir_sans_drafts
                ]
                extra_ctxs.extend(post_ctxs)
                extra_ctxs.extend(
                    [
                        ("index.html", partial(indexed_articles, dir_path=post_dir)),
                        # ("index.html", partial(indexed_article_series, dir_path=post_dir)),
                    ]
                )
            success = cut_templates(
                template_dir=template_dir,
                out_dir=site_dir,
                contexts=extra_ctxs,
                audit_builder=audit_builder,
            )
            if success:
                log(f"Built {template_dir}")
                if audit_builder.active:
                    audit_builder.auditer.write_delta()
            else:
                log(f"Failed to build {template_dir}")


def fmt_mtime(path_to_file):
    mtime = path_to_file.stat().st_mtime
    date = dt.fromtimestamp(mtime)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def update_ctx_count(name):
    global GLOBAL_CTX_COUNT
    GLOBAL_CTX_COUNT.setdefault(name, 0)
    GLOBAL_CTX_COUNT[name] += 1
    return


def multirow_corruption_error(indexed_file):
    err_msg = f"Corrupt audit log: multiple rows for the same input file {indexed_file}"
    raise ValueError(err_msg)


def check_audit(
    template,
    template_dir: Path,
    auditer: Auditer,
    known_upstream: Path | None = None,
) -> bool:
    """
    We only want to render (here we'll say "generate") things that are either:
    - not in the audit list (meaning they are newly created)
    - in the audit list with a different input hash (meaning they changed)

    We also want to remove anything from the audit list that isn't rendered i.e. when
    the input file is deleted, we want to remove its record too

    Therefore we will make a new audit log, adding records for each rendered item
    (enabling us to check after finishing if any that were on record are no longer).

    We will skip renders when the input hash on record matches, so long as the file's
    template hash on record also matches (which we track as the 'upstream' file).

    Where we can't specify the upstream dependency, for now we will assume that it has
    complex dependency, and always prefer to regenerate it. For example: some
    `index.html` files are generated based on the articles in a series and partial
    templates of footer content. Since there is not a single path we can check, we
    won't assume it's unchanged (always regenerate it), erring on the side of caution.
    """
    # TODO use dataclass rather than passing audit, reaudit, and location of layout
    # used as template (which is needed to do second order hash of 'upstream')
    # TODO: use the template changelog idea
    # To avoid repeatedly checking template files, we will keep a dict of
    # these, and look up the result in the dict rather than re-check them.
    template_changelog = {}
    log(f"Checking audit log for {template}")
    template_p = Path(template.filename)
    template_subp = template_p.relative_to(template_dir)
    f_in_log_match = auditer.log[auditer.log.f_in == str(template_subp)]
    input_sum = auditer.checksum(template_p)
    new_record = {
        "f_in": str(template_subp),
        "f_up": None,
        "f_out": None,
        "h_in": input_sum,
        "h_out": None,
    }
    record_df = pd.DataFrame.from_records([new_record])
    if f_in_log_match.empty:
        # There is no record of the file in the audit log
        log(f"No record: {template_subp}")
        # TODO: move this to somewhere that collects contexts, so we can distinguish
        # those with an upstream from those without (like `index.html` which doesn't
        # render from markdown but gets filled in as its own jinja template)
        generate_output = True
    else:
        # The file is recorded in the audit log: check for change
        log(f"Found record: {template_subp}")
        # Validate the match
        if len(f_in_log_match) > 1:
            log(f"Multi-row match for {template_subp}")
            multirow_corruption_error(template_subp)
        f_in_log_record = f_in_log_match.squeeze()
        if input_sum == f_in_log_record.h_in:
            # It's identical: the input file itself has not changed since last audited
            f_up = f_in_log_record.f_up
            if pd.isnull(f_up):
                # don't assume absence of upstream dependency that may have changed
                generate_output = True
            else:
                f_up_log_record = validate_audit_result(
                    auditer=auditer, rel_fp=f_up, down_rel_fp=template_subp
                )
                breakpoint()
                upstream_p = template_dir / f_up
                # Regenerate if the upstream changed
                generate_output = auditer.checksum(upstream_p) != f_up_log_record.h_in
        else:
            # It's changed
            generate_output = True
    auditer.new = pd.concat([auditer.new, record_df], ignore_index=True)
    return generate_output


# TODO: turn validate_audit_result into an Auditer method
# (NB: multirow_corruption_error lives in this module, move it too)
def validate_audit_result(
    auditer: Auditer, rel_fp: Path, down_rel_fp: Path | None = None
) -> pd.Series:
    log_match = auditer.log[auditer.log.f_in == str(rel_fp)]
    if len(log_match) > 1:
        err_msg = f"Multi-row match for {rel_fp}"
        if down_rel_fp is not None:
            err_msg += f" (upstream of {down_rel_fp})"
        log(err_msg)
        # Raise an error, do not return the record Series
        multirow_corruption_error(rel_fp)
    log_record = log_match.squeeze()
    return log_record


def base(
    template,
    template_dir: Path,
    audit_builder: AuditBuilder,
):
    """A context providing the template date"""
    log(f"Rendering {template} (base)")
    if audit_builder.active:
        generate_flag = check_audit(
            template, template_dir=template_dir, auditer=audit_builder.auditer
        )
    else:
        generate_flag = True
    update_ctx_count(name="base")
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
        "base_generate": generate_flag,
    }


def index(template):
    # Unclear if this is used...? Provides no context info
    log(f"Rendering {template} (index)")
    return {}


def indexed_article_series(template, dir_path, drop_hidden=True):
    "Sort article series by date"
    series_dict = {
        "series": sorted(
            [
                article_series(a, is_path=True)
                for a in dir_path.iterdir()
                if a.is_dir()  # sub-directory
                if (a / "index.md").exists()
                if not a.name.startswith("_")  # not partial template
            ],
            key=lambda d: dateparser.parse(d["date"]),
            reverse=True,
        )
    }
    if drop_hidden:
        series_dict = {
            "series": [
                article_series
                for article_series in series_dict["series"]
                if (
                    "hidden" not in article_series
                    or article_series["hidden"] is not True
                )
            ]
        }
    return series_dict


def indexed_articles(template, dir_path, with_series=True):
    "Sort articles by date"
    articles_dict = {
        "articles": sorted(
            [
                article(a, is_path=True)
                for a in dir_path.iterdir()
                if not a.is_dir()  # not sub-directory
                if not a.name.startswith("_")  # not partial template
            ],
            key=lambda d: dateparser.parse(d["date"]),
            reverse=True,
        )
    }
    if with_series:
        series_dict = indexed_article_series(template, dir_path)
        articles_dict = {
            "articles": sorted(
                [
                    *articles_dict["articles"],
                    *series_dict["series"],
                ],
                key=lambda d: dateparser.parse(d["date"]),
                reverse=True,
            )
        }
    return articles_dict


def article_series(template, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    log(f"Rendering {template} (article series)")
    update_ctx_count(name="article_series")
    template_path = template if is_path else Path(template.filename)
    template_index_path = template_path / "index.md"
    if not template_index_path.exists():
        raise ValueError(
            "Metadata is not supported for non-markdown articles (index.md not found)"
        )
    md_content = frontmatter.load(template_index_path)
    metadata = md_content.metadata
    required_keys = {"title", "desc", "date"}
    if not all(k in metadata for k in required_keys):
        raise ValueError(
            f"{template=} missing one or more of {required_keys=} in index.md"
        )
    return {"url": template_path.stem, "mtime": fmt_mtime(template_path), **metadata}


def article(template, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    log(f"Rendering {template} (article)")
    update_ctx_count(name="article")
    template_path = template if is_path else Path(template.filename)
    if template_path.suffix != ".md":
        raise ValueError("Metadata is not supported for non-markdown articles")
    md_content = frontmatter.load(template_path)
    metadata = md_content.metadata
    required_keys = {"title", "desc", "date"}
    if not all(k in metadata for k in required_keys):
        raise ValueError(f"{template=} missing one or more of {required_keys=}")
    return {"url": template_path.stem, "mtime": fmt_mtime(template_path), **metadata}


def convert_markdown(markdown: str):
    return markdowner.convert(markdown)


def md_context(template):
    """A context providing the parsed HTML and scanning it for KaTeX"""
    log(f"Rendering {template} (md context)")
    update_ctx_count(name="md_context")
    md_content = frontmatter.load(template.filename)
    html_content = convert_markdown(md_content.content)
    has_katex = """<span class="katex">""" in html_content
    return {"post_content_html": html_content, "katex": has_katex}


def render_md(site, template, **kwargs):
    """A rule that receives the union of context dicts as kwargs"""
    if "/drafts/" in template.name:
        return
    log(f"Rendering {template} (md)")
    update_ctx_count(name="render_md")
    # i.e. posts/post1.md -> build/posts/post1.html
    template_out_as = Path(template.name).relative_to(Path(POST_DIRNAME))
    out_parts = list(template_out_as.parts)
    is_index = template_out_as.stem == "index"
    is_multipart = len(out_parts) > 1
    if is_multipart:
        if is_index:
            out_parts.pop()  # Remove the index, giving it the parent dir as its path
        template_out_as = Path("-".join(out_parts))
    # URLs do not have to end with .html so do not add suffix other than for index file
    # Multipart indexes drop the index name but for suffix we still treat the same
    out_suffix = ".html" if (is_index and not is_multipart) else ""
    out = site.outpath / template_out_as.with_suffix(out_suffix)
    # Compile and stream the result
    upstream_template = "layouts/_post.html"
    site.get_template(upstream_template).stream(**kwargs).dump(
        str(out), encoding="utf-8"
    )


def cut_templates(
    template_dir: Path,
    out_dir: Path,
    audit_builder: AuditBuilder,
    contexts: list[tuple[str, Callable]] | None = None,
    mergecontexts: bool = True,
) -> bool:
    base_loaded = partial(base, template_dir=template_dir, audit_builder=audit_builder)
    default_ctxs = [
        (r".*\.(html|md)$", base_loaded),
        ("index.html", index),
        (r".*\.md", md_context),
    ]
    custom_contexts = contexts or []
    contexts = default_ctxs + custom_contexts
    site = Site.make_site(
        contexts=contexts,
        mergecontexts=mergecontexts,
        searchpath=template_dir,
        outpath=out_dir,
        rules=[(r".*\.md", render_md)],
    )
    try:
        site.render()
    except BaseException as exc:
        logging.info("Failed to render site", exc_info=True)
        log(f"\nFAIL: {exc}\n")
        success = False
    else:
        success = True
    finally:
        log(f"CTX COUNTS: {GLOBAL_CTX_COUNT}")
        return success
