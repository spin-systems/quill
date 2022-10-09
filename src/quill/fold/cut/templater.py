import logging
from datetime import datetime as dt
from functools import partial
from pathlib import Path

import dateparser
import frontmatter
import markdown
from staticjinja import Site

from ..ns_util import ns, ns_path

__all__ = ["standup"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pymd_extensions = "fenced_code codehilite sane_lists def_list".split()
markdowner = markdown.Markdown(output_format="html5", extensions=pymd_extensions)

OUT_DIRNAME = "site"
TEMPLATE_DIRNAME = "src"
POST_DIRNAME = "posts"


def standup(domains_list=None, verbose=True):
    domains_list = domains_list or [*ns]
    for domain in domains_list:
        ns_p = ns_path / domain
        if not ns_p.exists() and ns_p.is_dir():
            raise ValueError(f"{ns_p} not found")
        template_dir = ns_p / TEMPLATE_DIRNAME
        if template_dir.exists():
            site_dir = ns_p / OUT_DIRNAME
            post_dir = template_dir / POST_DIRNAME
            extra_ctxs = []
            if post_dir.exists():
                post_dir_sans_drafts = [
                    a for a in post_dir.iterdir() if a.name != "drafts"
                ]
                for a in post_dir_sans_drafts:
                    logger.info(f"POST: {a}")
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
            cut_templates(
                template_dir=template_dir, out_dir=site_dir, contexts=extra_ctxs
            )
            logger.info(f"Built {template_dir}")


def fmt_mtime(path_to_file):
    mtime = path_to_file.stat().st_mtime
    date = dt.fromtimestamp(mtime)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def base(template):
    logger.info(f"Rendering {template} (base)")
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
    }


def index(template):
    logger.info(f"Rendering {template} (index)")
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
    logger.info(f"Rendering {template} (article series)")
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
    logger.info(f"Rendering {template} (article)")
    template_path = template if is_path else Path(template.filename)
    if template_path.suffix != ".md":
        raise ValueError("Metadata is not supported for non-markdown articles")
    md_content = frontmatter.load(template_path)
    metadata = md_content.metadata
    required_keys = {"title", "desc", "date"}
    if not all(k in metadata for k in required_keys):
        raise ValueError(f"{template=} missing one or more of {required_keys=}")
    return {"url": template_path.stem, "mtime": fmt_mtime(template_path), **metadata}


def md_context(template):
    logger.info(f"Rendering {template} (md context)")
    # markdown_content = Path(template.filename).read_text()
    md_content = frontmatter.load(template.filename)
    return {"post_content_html": markdowner.convert(md_content.content)}


def render_md(site, template, **kwargs):
    if "/drafts/" in template.name:
        return
    logger.info(f"Rendering {template} (md)")
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


def cut_templates(template_dir, out_dir, contexts=None, mergecontexts=True):
    default_ctxs = [
        (r".*\.(html|md)$", base),
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
