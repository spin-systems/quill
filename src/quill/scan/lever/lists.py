from .blockelems import BlockList
from .tokens import Prefix, Suffix

__all__ = ["parse_nodes_to_list"]

def create_BlockList(nodes, has_header):
    "Simple wrapper to turn boolean has_header into a header Node argument"
    header = nodes.pop(0) if has_header else None
    return BlockList(nodes, header)

def parse_nodes_to_list(nodes):
    """
    Generator function which yields all lists per block, ignoring any intervening
    or pre/succeeding non-list nodes (except any directly preceding 'header' node,
    with a line-terminating colon marked as `Suffix.ListInit`).
    """
    nodes = nodes.copy() # do not modify input!
    list_open = list_header_open = False
    has_header = False
    parsed = [] # nodes belonging to a list go here
    while nodes: # unlike a for loop, allows passing any remaining `nodes` upon return
        node = nodes.pop(0)
        if list_open:
            # very crudely, just terminate on any non-list continuation item
            if node.prefix is Prefix.ContList:
                parsed.append(node)
            else:
                list_open = False # list terminates
                # a break here would skip any remaining nodes, requiring func recursion
                # to capture multiple lists per block, a yield is the preferable option
                yield create_BlockList(parsed, has_header)
                has_header = False # reset this in case parsing another list in block
                parsed = []
        elif list_header_open:
            if node.prefix == Prefix.InitList:
                list_header_open = False
                list_open = True
                parsed.append(node)
        else:
            if node.suffix == Suffix.InitList:
                list_header_open = has_header = True
                parsed.append(node)
            elif node.prefix == Prefix.InitList:
                if list_header_open:
                    list_header_open = False
                list_open = True
                parsed.append(node)
    if parsed:
        yield create_BlockList(parsed, has_header)
