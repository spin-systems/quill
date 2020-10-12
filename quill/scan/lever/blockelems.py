from .elems import BaseElem

class BlockElem(BaseElem):
    "Base class for any block-level element."
    #def __init__(self, nodelist):
    #    super().__init__(nodelist)

class BlockList(BlockElem):
    """
    A block-level list would be a list of `ListInit`-prefixed
    nodes and could have a `ListInit`-suffixed header node.

    If initialised in the midst of a different element type, pass its
    element type (block- or doc-level) through `parent_elem` argument.
    """
    def __init__(self, nodes, parent_elem=None):
        list_nodes = parse_list(nodes)
        super().__init__(list_nodes) # once sublist of nodes determined

def parse_nodes_to_list(nodes):
    """
    Parses one list per block, returning any 'unattached' nodes after
    the list's termination, which can be passed again [recursively]
    until the function exhausts the block (either finding further list
    elements or reaching the final node of the block).
    """
    list_open = False
    parsed = [] # nodes belonging to a list go here
    while nodes: # unlike a for loop, allows passing any remaining `nodes` upon return
        node = nodes.pop(0)
        if list_open:
            if node.prefix in list_terminating_prefixes:
                list_open = False
                break # Skip remaining nodes once a list has terminated
        elif list_header_open:
            if node.prefix == Prefix.InitList:
                list_header_open = False
                list_open = True
        else:
            if node.suffix == Suffix.InitList:
                list_header_open = True
                parsed.append(node)
            elif node.prefix == Prefix.InitList:
                if list_header_open:
                    list_header_open = False
                list_open = True
                parsed.append(node)

