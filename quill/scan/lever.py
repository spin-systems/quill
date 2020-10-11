from .tokens import tokenise_line, Prefix, Node
from .structure import ParsedDoc
from .blockelems import * # temporary
from .docelems import * # temporary

__all__ = ["MMD"]

class MMD:
    def __init__(self, mmd_lines):
        self.doc = ParsedDoc(mmd_lines)

    def __repr__(self):
        return f"Parsed MMD file ({self.doc})"
