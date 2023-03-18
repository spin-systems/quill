from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Callable

from ...__share__ import Logger
from ..auditing import AuditBuilder
from .contexts import article, base, date_indexed_articles, index, md_context
from .name_config import POST_DIRNAME

__all__ = ["get_default_ctxs", "get_post_ctxs"]

Log = Logger(__name__).Log


def get_default_ctxs(
    template_dir: Path, *, audit_builder: AuditBuilder
) -> list[tuple[str, Callable]]:
    base_loaded = partial(base, template_dir=template_dir, audit_builder=audit_builder)
    index_loaded = partial(index, audit_builder=audit_builder)
    md_loaded = partial(md_context, audit_builder=audit_builder)
    default_ctxs = [
        (r".*\.(html|md)$", base_loaded),
        ("index.html", index_loaded),
        (r".*\.md", md_loaded),
    ]
    return default_ctxs


def get_post_ctxs(
    template_dir: Path, *, audit_builder: AuditBuilder
) -> list[tuple[str, Callable]]:
    post_dir = template_dir / POST_DIRNAME
    indexed_post_ctxs = []
    article_loaded = partial(article, audit_builder=audit_builder)
    date_indexed_articles_loaded = partial(
        date_indexed_articles, audit_builder=audit_builder
    )
    if post_dir.exists():
        post_dir_sans_drafts = [a for a in post_dir.iterdir() if a.name != "drafts"]
        # for a in post_dir_sans_drafts:
        #     Log(f"POST: {a}")
        post_leaf_dir = Path(POST_DIRNAME)
        post_ctxs = [
            (str(post_leaf_dir / a.name), article_loaded) for a in post_dir_sans_drafts
        ]
        indexed_post_ctxs.extend(post_ctxs)
        indexed_post_ctxs.extend(
            [("index.html", partial(date_indexed_articles_loaded, dir_path=post_dir))]
        )
    return indexed_post_ctxs
