from __future__ import annotations

from pathlib import Path

import dateparser
import frontmatter

from ...__share__ import Logger
from ..auditing import AuditBuilder
from .audit_checking import check_audit
from .ctx import update_ctx_count
from .datetime_util import fmt_mtime
from .pymd_engine import convert_markdown

__all__ = [
    "base",
    "index",
    "date_indexed_article_series",
    "date_indexed_articles",
    "article_series",
    "article",
    "md_context",
]

Log = Logger(__name__).Log


def base(
    template,
    template_dir: Path,
    audit_builder: AuditBuilder,
):
    """A context providing the template date"""
    if audit_builder.active:
        if audit_builder.auditer.recheck and audit_builder.auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} (base)")
            return {}
    Log(f"- Prepping {template} (base)")
    if audit_builder.active:
        generate_flag = check_audit(
            template, template_dir=template_dir, auditer=audit_builder.auditer
        )
        if not generate_flag:
            Log(f"  ! Identified no regeneration: {template}")
    else:
        generate_flag = True
    update_ctx_count(name="base")
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
        "base_generate": generate_flag,
        "audit_builder": audit_builder,
        "template_dir": template_dir,
    }


def index(template, audit_builder: AuditBuilder):
    """Strongly suspect this doesn't actually do anything..."""
    # TODO: check effect of removal
    if audit_builder.active:
        if audit_builder.auditer.recheck and audit_builder.auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} (index)")
            return {}
    Log(f"- Prepping {template} (index)")
    return {}


def date_indexed_article_series(template, dir_path, drop_hidden=True):
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


def date_indexed_articles(
    template, dir_path, audit_builder: AuditBuilder, with_series=True
):
    "Sort articles by date"
    if audit_builder.active:
        if audit_builder.auditer.recheck and audit_builder.auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} (article)")
            return {}
    articles_dict = {
        "articles": sorted(
            [
                article(a, audit_builder=audit_builder, is_path=True)
                for a in dir_path.iterdir()
                if not a.is_dir()  # not sub-directory
                if not a.name.startswith("_")  # not partial template
            ],
            key=lambda d: dateparser.parse(d["date"]),
            reverse=True,
        )
    }
    if with_series:
        series_dict = date_indexed_article_series(template, dir_path)
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
    Log(f"- Prepping {template} (article series)")
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


def article(template, audit_builder: AuditBuilder, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    if audit_builder.active:
        if audit_builder.auditer.recheck and audit_builder.auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} (article)")
            return {}
    Log(f"- Prepping {template} (article)")
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


def make_toc(index_path: Path) -> list[tuple[str, str]]:
    toc_list = [
        (
            matter.metadata.get("order", -1),
            matter.metadata["title"],
            f"{index_path.parent.stem}-{series_entry.stem}",
        )
        for series_entry in index_path.parent.iterdir()
        if series_entry != index_path
        if not series_entry.is_dir()
        for matter in [frontmatter.load(series_entry)]
    ]
    toc_list.sort()
    return toc_list


def md_context(template, audit_builder: AuditBuilder):
    """A context providing the parsed HTML and scanning it for KaTeX"""
    if audit_builder.active:
        if audit_builder.auditer.recheck and audit_builder.auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} (md context)")
            return {}  # Avoid reading markdown files if not going to render them!
    Log(f"- Prepping {template} (md context)")
    update_ctx_count(name="md_context")
    md_content = frontmatter.load(template.filename)
    html_content = convert_markdown(md_content.content)
    has_katex = """<span class="katex">""" in html_content
    series_toc_magic = "%series_toc%"
    has_series_toc = series_toc_magic in html_content
    extra_flags = {"katex": has_katex}
    if has_series_toc:
        html_content = html_content.replace(series_toc_magic, "")
        series_toc_list = make_toc(index_path=Path(template.filename))
        extra_flags["series_toc"] = series_toc_list
    return {"post_content_html": html_content, **extra_flags}
