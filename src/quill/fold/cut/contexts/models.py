from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd  # noqa: F401
from jinja2 import Template
from pydantic import BaseModel, Field
from pydantic.types import FilePath

from ...auditing import AuditBuilder, Auditer  # noqa: F401
from ..audit_checking import check_audit
from ..datetime_util import fmt_mtime

__all__ = [
    "RequiredMDMetadata",
    "MDMetadata",
    "BaseContext",
    "ArticleContext",
    "MdContext",
    "ArticleSeries",
    "TemplateInfo",
]


class RequiredMDMetadata(BaseModel, extra="forbid"):
    """The required keys for markdown file metadata (not exhaustive)."""

    title: str
    desc: str
    date: str | int


class MDMetadata(RequiredMDMetadata, extra="forbid"):
    """The total data model for markdown file metadata (exhaustive)."""

    gh: str = None
    rtd: str = None
    hidden: bool = None
    shortcite: str = None
    inproceedings: str = None
    pypi: str = None
    link: str = None
    stack: list[str] = None
    size: int = None
    topic: str = None
    generate_footer: bool = Field(None, validation_alias="generate-footer")
    generate_toc: bool = Field(None, validation_alias="generate-toc")
    generate_teaser: bool = Field(None, validation_alias="generate-teaser")
    index: int = None
    order: int = None


class BaseContext(BaseModel, arbitrary_types_allowed=True):
    template_date: datetime
    base_generate: bool
    audit_builder: AuditBuilder
    template_dir: Path

    @classmethod
    def from_ctx(
        cls, template: Template, template_dir: Path, audit_builder: AuditBuilder
    ) -> BaseContext:
        auditer = audit_builder.auditer
        base_generate = (
            check_audit(template, template_dir=template_dir, auditer=auditer)
            if audit_builder.active
            else True
        )
        return cls(
            template_date=fmt_mtime(Path(template.filename)),
            base_generate=base_generate,
            audit_builder=audit_builder,
            template_dir=template_dir,
        )


class ArticleContext(BaseModel, arbitrary_types_allowed=True):
    url: str
    mtime: datetime

    @classmethod
    def from_ctx(cls, template: Path) -> ArticleContext:
        return cls(url=template.stem, mtime=fmt_mtime(template))


class MdContext(BaseModel, arbitrary_types_allowed=True):
    post_content_html: str
    katex: bool
    series_toc: list[tuple[int, str, str]] = None


class ArticleSeries(BaseModel):
    title: str
    desc: str
    date: str
    hidden: bool = False


class TemplateInfo(BaseModel):
    index_path: FilePath
