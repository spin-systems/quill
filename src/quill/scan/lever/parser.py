from .structure import BlockDoc
from .blockelems import *  # temporary
from .docelems import DocLists
from .lists import parse_nodes_to_list, SepBlockList
from pandas import concat, DataFrame as DF

__all__ = ["Doc"]

class PartsList(list):
    def __init__(self, parts, part_keys=None):
        self.extend(parts)
        self.part_keys = part_keys

    def as_df(self):
        pk = self.part_keys
        df = concat([DF.from_dict(dict(zip(pk, [[e] for e in p]))) for p in self])
        return df.reset_index().drop("index", 1)

class Doc(BlockDoc):
    def __init__(self, lines, listparseconfig=None):
        super().__init__(lines)  # block tokenisation pass, creating nodes property
        self._parse(listparseconfig)  # tokenised block parsing, creating lists property

    def _parse(self, listparseconfig=None):
        # populate the `lists` property by parsing all blocks' nodes
        self._parse_lists(listparseconfig)

    def _parse_lists(self, listparseconfig=None):
        all_blocklists = []
        for block in self.blocks:
            nodes = block.nodes
            # yields blocklist objects
            blocklist_generator = parse_nodes_to_list(nodes, listparseconfig)
            blocklists = list(blocklist_generator)  # exhaust generator
            all_blocklists.extend(blocklists)  # flat list: all BlockList objects in Doc
        # `DocLists` object from list of BlockList objects
        self.lists = DocLists(all_blocklists)
        if (
            listparseconfig
            and "listclass" in listparseconfig
            and listparseconfig.get("listclass") is SepBlockList
        ):
            pk = ("domain", "repo_name", "priority") # hard code for now
            # N.B. maybe use an Enum rather than have to pass actual class?
            self.all_parts = PartsList([
                n.parts
                for l in self.lists
                for n in (l.all_nodes if l.has_sep_header else l.nodes)
            ], part_keys=pk)
        # TODO: wasteful to store nodes twice: just store index for header/list items

    @property
    def lists(self):
        # What I really want here is the union, over all blocks in the Doc,
        # of each's block's lines' output from parse_nodes_to_list
        # which will probably necessitate a more complicated structure,
        # in some dedicated class which manages lists by block
        return self._lists

    @property
    def list(self):
        if len(self.lists) == 1:
            return self.lists[0]
        else:
            return None

    @lists.setter
    def lists(self, ll):
        self._lists = ll

    @property
    def _doc_repr(self):
        "Private property to enable access from MMD superclass"
        block_repr = super().__repr__()
        cont = ", containing "
        parsed_list_repr = self.lists.repr_str if self.lists else ""
        parsed_repr = f"{cont}{parsed_list_repr}" if self.lists else ""
        return f"{block_repr}{parsed_repr}"

    def __repr__(self):
        return self._doc_repr
