from .elems import BaseElem

class BlockElem(BaseElem):
    "Base class for any block-level element."
    def __init__(self, nodelist):
        super().__init__(nodelist)
        self.nodes = nodelist

class BlockList(BlockElem):
    """
    A block-level list would be a list of `ListInit`-prefixed nodes and
    could have a `ListInit`-suffixed header node.
    """
    def __init__(self, nodelist):
        super().__init__(nodelist)
