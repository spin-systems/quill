from __future__ import annotations

from pathlib import Path

import dateparser
from pydantic import TypeAdapter, ValidationError
from pydantic.types import DirectoryPath, FilePath

from ....__share__ import Logger
from ...auditing import AuditBuilder
from .helpers import audit_template, log_template, skip_auditer
from .md import load_md_meta
from .models import ArticleContext

__all__ = [
    "date_indexed_article_series",
    "date_indexed_articles",
    "article_series",
    "article",
]

Log = Logger(__name__).Log


def validate_series_dir(
    cls: type[FilePath] | type[DirectoryPath], path: Path, why: str
) -> bool:
    try:
        TypeAdapter(cls).validate_python(path)
    except ValidationError:
        Log(f" (!) Invalid series directory ({why}) {path}")
        return False
    else:
        Log(f" (?) Valid series directory (not {why}) {path}")
        return True


def is_valid_series_directory(path: Path) -> bool:
    exists = validate_series_dir(DirectoryPath, path, why="doesn't exist")
    has_index = validate_series_dir(FilePath, path / "index.md", why="no index")
    hidden = path.name.startswith("_")
    return exists and has_index and not hidden


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
    metadata = load_md_meta(index_path)
    ctx = ArticleContext.from_ctx(template_path).model_dump()
    return {**ctx, **metadata}


@audit_template
def article(template, audit_builder: AuditBuilder, is_path=False):
    """A context providing the URL, time last modified, and all frontmatter metadata"""
    template_path = template if is_path else Path(template.filename)
    if template_path.suffix != ".md":
        raise ValueError("Metadata is not supported for non-markdown articles")
    metadata = load_md_meta(template_path)
    ctx = ArticleContext.from_ctx(template_path).model_dump()
    return {**ctx, **metadata}
