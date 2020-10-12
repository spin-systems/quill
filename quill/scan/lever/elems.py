class BaseElem:
    "Base class for any element (both block-level and doc-level)."
    def __init__(self, nodes):
        self.nodes = nodes
