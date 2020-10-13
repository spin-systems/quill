from .structure import BlockDoc
from .blockelems import * # temporary
from .docelems import DocLists
from .lists import parse_nodes_to_list

__all__ = ["Doc"]

class Doc(BlockDoc):
    def __init__(self, lines):
        super().__init__(lines) # block tokenisation pass, creating nodes property
        self.parse() # tokenised block parsing pass, creating lists property (etc.)

    def parse(self):
        self.parse_lists() # populate the `lists` property by parsing all blocks' nodes

    def parse_lists(self):
        all_blocklists = []
        for block in self.blocks:
            nodes = block.nodes
            blocklist_generator = parse_nodes_to_list(nodes) # yields blocklist objects
            blocklists = list(blocklist_generator) # exhaust generator
            all_blocklists.extend(blocklists) # flat list: all BlockList objects in Doc
        # `DocLists` object from list of BlockList objects
        self.lists = DocLists(all_blocklists) 
        # TODO: wasteful to store nodes twice: just store index for header/list items

    @property
    def lists(self):
        # What I really want here is the union, over all blocks in the Doc,
        # of each's block's lines' output from parse_nodes_to_list
        # which will probably necessitate a more complicated structure,
        # in some dedicated class which manages lists by block
        return self._lists

    @lists.setter
    def lists(self, ll):
        self._lists = ll

    def __repr__(self):
        block_repr = super().__repr__()
        cont = ", containing "
        parsed_list_repr = self.lists.repr_str if self.lists else ""
        parsed_repr = f"{cont}{parsed_list_repr}" if self.lists else ""
        return f"{block_repr}{parsed_repr}"
