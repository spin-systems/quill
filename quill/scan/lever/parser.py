from .structure import BlockDoc
from .blockelems import * # temporary
from .docelems import * # temporary

__all__ = ["Doc"]

class Doc(BlockDoc):
    def __init__(self, lines):
        super().__init__(lines) # block tokenisation pass

    def __repr__(self):
        block_repr = super().__repr__()
        parsed_repr = "1 list (EXAMPLE)"
        return f"{block_repr}, containing {parsed_repr}"
