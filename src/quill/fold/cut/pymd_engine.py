from __future__ import annotations

import markdown

__all__ = ["convert_markdown"]


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


def convert_markdown(markdown: str):
    return markdowner.convert(markdown)
