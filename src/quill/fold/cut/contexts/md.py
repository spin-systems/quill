from __future__ import annotations

from pathlib import Path

from frontmatter import load
from pydantic import TypeAdapter, ValidationError
from pydantic.types import FilePath

from ....__share__ import Logger
from ...auditing import AuditBuilder
from ..pymd_engine import convert_markdown
from .helpers import audit_template, log_template
from .models import MdContext, MDMetadata

__all__ = ["make_toc", "md_context"]

Log = Logger(__name__).Log


def make_toc(index_path: Path) -> list[tuple[int, str, str]]:
    toc_list = [
        (
            matter.metadata.get("order", -1),
            matter.metadata["title"],
            f"{index_path.parent.stem}-{series_entry.stem}",
        )
        for series_entry in index_path.parent.iterdir()
        if series_entry != index_path
        if not series_entry.is_dir()
        for matter in [load(series_entry)]
    ]
    return sorted(toc_list)


@log_template
@audit_template
def md_context(template, audit_builder: AuditBuilder):
    """A context providing the parsed HTML and scanning it for KaTeX"""
    md_content = load(template.filename)
    html_content = convert_markdown(md_content.content)
    has_katex = """<span class="katex">""" in html_content
    kwargs = {}
    if (series_toc_magic := "%series_toc%") in html_content:
        html_content = html_content.replace(series_toc_magic, "")
        kwargs["series_toc"] = make_toc(index_path=Path(template.filename))
    ctx = MdContext(post_content_html=html_content, katex=has_katex, **kwargs)
    return ctx.model_dump()


def load_md_meta(md: FilePath) -> dict:
    TypeAdapter(FilePath).validate_python(md)
    md_content = load(md)
    validated = MDMetadata.model_validate(md_content.metadata)
    return validated.model_dump()
