from .elems import BaseElem

class DocElem(BaseElem):
    "Base class for any doc-level element."
    def __init__(self, nodelist):
        self.nodes = nodelist

class DocList(DocElem):
    """
    A doc-level list could be a list of header-prefixed nodes and
    could have a `ListInit`-suffixed header node.
    """
    def __init__(self, nodelist):
        super().__init__(nodelist)
