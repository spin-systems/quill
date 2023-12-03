from __future__ import annotations

from pathlib import Path

import dateparser
import frontmatter
from pydantic import TypeAdapter
from pydantic.types import FilePath

from ....__share__ import Logger
from ...auditing import AuditBuilder
from ..datetime_util import fmt_mtime
from .helpers import audit_template, log_template, skip_auditer
from .models import MDMetadata

__all__ = [
    "date_indexed_article_series",
    "date_indexed_articles",
    "article_series",
    "article",
]

Log = Logger(__name__).Log


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
