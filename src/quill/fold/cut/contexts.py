from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Callable

import dateparser
import frontmatter
from jinja2 import Template
from pydantic import BaseModel, TypeAdapter
from pydantic.types import FilePath

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


def log_template(func: Callable):
    @wraps(func)
    def wrapper(template: Template, *args, **kwargs):
        Log(f"- Prepping {template} ({func.__name__})")
        update_ctx_count(name=func.__name__)
        return func(template, *args, **kwargs)

    return wrapper


def skip_auditer(
    audit_builder: AuditBuilder, template: Template, func_name: str
) -> bool:
    if audit_builder.active:
        auditer = audit_builder.auditer
        if auditer.recheck and auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} ({func_name})")
            return True
    return False


def audit_template(func):
    @wraps(func)
    def wrapper(template, audit_builder, *args, **kwargs):
        if skip_auditer(audit_builder, template, func.__name__):
            return {}
        return func(template, audit_builder, *args, **kwargs)

    return wrapper


@log_template
def base(
    template,
    template_dir: Path,
    audit_builder: AuditBuilder,
):
    """A context providing the template date"""
    if skip_auditer(audit_builder, template, "base"):
        return {}
    if audit_builder.active:
        generate_flag = check_audit(
            template, template_dir=template_dir, auditer=audit_builder.auditer
        )
        if not generate_flag:
            Log(f"  ! Identified no regeneration: {template}")
    else:
        generate_flag = True
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
        "base_generate": generate_flag,
        "audit_builder": audit_builder,
        "template_dir": template_dir,
    }


@log_template
@audit_template
def index(template, audit_builder: AuditBuilder):
    """The home/front page (main subdomain index page)."""
    return {}


def is_valid_series_directory(path: Path) -> bool:
    return (
        path.is_dir() and (path / "index.md").exists() and not path.name.startswith("_")
    )


def sort_by_date(records: list[dict]) -> list[dict]:
    return sorted(records, key=lambda d: dateparser.parse(d["date"]), reverse=True)


def date_indexed_article_series(template, dir_path, drop_hidden=True):
    "Sort article series by date"
    unsorted_series_list = [
        article_series(series_path, is_path=True)
        for series_path in dir_path.iterdir()
        if is_valid_series_directory(path=series_path)
    ]
    results = sort_by_date(unsorted_series_list)
    if drop_hidden:
        pruned_series_list = [
            article_series
            for article_series in results
            if ("hidden" not in article_series or article_series["hidden"] is not True)
        ]
        results = pruned_series_list
    return results


def date_indexed_articles(
    template, dir_path, audit_builder: AuditBuilder, with_series=True
):
    "Sort articles by date"
    if skip_auditer(audit_builder, template, "article"):
        return {}
    unsorted_articles = [
        article(a, audit_builder=audit_builder, is_path=True)
        for a in dir_path.iterdir()
        if not a.is_dir()  # not sub-directory
        if not a.name.startswith("_")  # not partial template
    ]
    sorted_articles = sort_by_date(unsorted_articles)
    if with_series:
        series_articles = date_indexed_article_series(template, dir_path)
        sorted_articles = sort_by_date([*sorted_articles, *series_articles])
    return {"articles": sorted_articles}


class MDMetadata(BaseModel):
    title: str
    desc: str
    date: str


class TemplateInfo(BaseModel):
    index_path: FilePath


@log_template
def article_series(template, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    template_path = template if is_path else Path(template.filename)
    index_path = TypeAdapter(FilePath).validate_python(template_path / "index.md")
    md_content = frontmatter.load(index_path)
    metadata = md_content.metadata
    validated = MDMetadata.model_validate(md_content.metadata)
    return {"url": template_path.stem, "mtime": fmt_mtime(template_path), **metadata}


@audit_template
def article(template, audit_builder: AuditBuilder, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    template_path = template if is_path else Path(template.filename)
    if template_path.suffix != ".md":
        raise ValueError("Metadata is not supported for non-markdown articles")
    md_content = frontmatter.load(template_path)
    metadata = md_content.metadata
    validated = MDMetadata.model_validate(md_content.metadata)
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


@log_template
@audit_template
def md_context(template, audit_builder: AuditBuilder):
    """A context providing the parsed HTML and scanning it for KaTeX"""
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
