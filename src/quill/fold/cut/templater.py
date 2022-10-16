from __future__ import annotations

import logging
from datetime import datetime as dt
from functools import partial
from pathlib import Path
from sys import stderr

import dateparser
import frontmatter
import markdown
import pandas as pd
from staticjinja import Site

from ..auditing import checksum, read_audit
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
                audit = read_audit(audit_p)
                reaudit = audit.drop(audit.index)
            else:
                audit = reaudit = None
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
            breakpoint()
            cut_templates(
                template_dir=template_dir,
                out_dir=site_dir,
                contexts=extra_ctxs,
                audit_log=audit,
                reaudit=reaudit,
            )
            log(f"Built {template_dir}")


def fmt_mtime(path_to_file):
    mtime = path_to_file.stat().st_mtime
    date = dt.fromtimestamp(mtime)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def update_ctx_count(name):
    global GLOBAL_CTX_COUNT
    GLOBAL_CTX_COUNT.setdefault(name, 0)
    GLOBAL_CTX_COUNT[name] += 1
    return


def check_audit(
    template,
    template_dir: Path,
    audit_log: pd.DataFrame | None,
    reaudit: pd.DataFrame | None,
):
    """
    We only want to render things that are either:
    - not in the audit list (meaning they are newly created)
    - in the audit list with a different input hash (meaning they changed)

    We also want to remove anything from the audit list that isn't rendered i.e. when
    the input file is deleted, we want to remove its record too

    Therefore we will make a new audit log, adding records for each rendered item,
    skipping renders when the input hash on record matches, (with one exception: if the
    file's template hash on record doesn't).
    """
    # TODO use dataclass rather than passing audit_log, reaudit, and location of layout
    # used as template (which is needed to do second order hash of 'upstream')
    input_files = audit_log.f_in.to_list()
    upstream_files = audit_log.f_up.unique().tolist()
    # To avoid repeatedly checking template files, we will keep a dict of
    # these, and look up the result in the dict rather than re-check them.
    template_changelog = {}
    log(f"Checking audit log for {template}")
    template_p = Path(template.filename)
    template_subp = template_p.relative_to(template_dir)
    matched_audit = audit_log[audit_log.f_in == template_subp]
    if matched_audit.empty:
        # There is no record of the file in the audit log
        log(f"No record: {template_subp}")
        breakpoint()
        # TODO: move this to somewhere that collects contexts, so we can distinguish
        # those with an upstream from those without (like `index.html` which doesn't
        # render from markdown but gets filled in as its own jinja template)
        new_record = {
            "f_in": str(template_subp),
            "f_up": None,
            "f_out": None,
            "h_in": checksum(template_p),
            "h_out": None,
        }
        record_df = pd.DataFrame.from_records([new_record])
        reaudit = pd.concat([reaudit, record_df], ignore_index=True)
    else:
        # The file is recorded in the audit log: check for change
        log(f"Found record: {template_subp}")
        breakpoint()
    return


def base(
    template,
    template_dir: Path,
    audit_log: pd.DataFrame | None,
    reaudit: pd.DataFrame | None,
):
    """A context providing the template date"""
    log(f"Rendering {template} (base)")
    if audit_log is not None:
        check_audit(
            template, template_dir=template_dir, audit_log=audit_log, reaudit=reaudit
        )
    update_ctx_count(name="base")
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
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
    site.get_template("layouts/_post.html").stream(**kwargs).dump(
        str(out), encoding="utf-8"
    )


def cut_templates(
    template_dir,
    out_dir,
    contexts=None,
    mergecontexts=True,
    audit_log=None,
    reaudit=None,
):
    base_loaded = partial(
        base, template_dir=template_dir, audit_log=audit_log, reaudit=reaudit
    )
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
    except:
        logging.info("Failed to render site", exc_info=True)
    log(f"CTX COUNTS: {GLOBAL_CTX_COUNT}")
