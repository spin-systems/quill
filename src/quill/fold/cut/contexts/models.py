from __future__ import annotations

from pydantic import BaseModel
from pydantic.types import FilePath

__all__ = ["MDMetadata", "ArticleSeries", "TemplateInfo"]


class MDMetadata(BaseModel):
    """The required keys for markdown file metadata (not exhaustive)."""

    title: str
    desc: str
    date: str


class ArticleSeries(BaseModel):
    title: str
    desc: str
    date: str
    hidden: bool = False


class TemplateInfo(BaseModel):
    index_path: FilePath
