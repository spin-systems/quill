from enum import Enum
from ...__share__ import classproperty

__all__ = []


def has_precedent(seen, prefix):
    """
    Check if there is a seen node with a given prefix.
    No need to do this for suffixes as their precedent only ever checked
    for directly preceding.
    """
    return any([n.prefix == prefix for n in seen])


def lever_config_dict():
    """
    Return default parser config
    """
    return {
        # Permit `Prefix.ListInit` without directly preceding `Suffix.ListInit`
        "ALLOW_LIST_WITHOUT_SUFFIX_INIT": True
    }


def tokenise_line(line, seen=None, config=None):
    """
    Follow rules for prefix and suffix token order, splitting
    the string into `(prefix, contents, suffix)`. Optionally
    specify `custom_config` dict to override defaults from
    `lever_config_dict`.
    """
    ############ Begin config instantation ###########
    default_config = lever_config_dict()
    if config:
        # Only allow custom config keys also present in default_config dict
        config = {k: v for k, v in config.items() if k in default_config}
        config = {**default_config, **config}  # override default config
    else:
        config = default_config
    ############## Read config variables ##############
    ALLOW_LIST_WITHOUT_SUFFIX_INIT = config.get("ALLOW_LIST_WITHOUT_SUFFIX_INIT")
    ############# End config instantation #############
    seen = seen if seen else []  # avoid default mutable arg gotcha
    has_history = len(seen) > 0  # preceding tokenised line(s)
    penultimate = seen[-1] if has_history else None  # directly preceding
    if line == "":
        return Node()  # Empty call passes all arguments with default value `None`
    else:
        node = Node(prefix=None, contents=line.rstrip("\n"), suffix=None)
        if line.startswith("-:"):
            if line[2] == "'":
                node.prefix = Prefix.Because
            elif line[2] == ".":
                node.prefix = Prefix.Therefore
            elif penultimate and penultimate.contents.endswith(":"):
                # Mark penultimate line's suffix as beginning a list
                penultimate.suffix = Suffix.InitList
                node.prefix = Prefix.InitList
            elif ALLOW_LIST_WITHOUT_SUFFIX_INIT:
                node.prefix = Prefix.InitList
            # (Question not implemented here)
        elif line.startswith("-,"):
            if line[2] == ":" and has_precedent(seen, Prefix.InitList):
                # For now consider a list 'open' indefinitely while the block is
                # i.e. until blank line (TODO implement break at section divider)
                node.prefix = Prefix.ContList
            elif line[2] == ",":
                node.prefix = Prefix.Ascent
            else:
                node.prefix = Prefix.FollowOn
        elif line.startswith("-."):
            if line[2] == ".":
                node.prefix = Prefix.Descent
            elif line[2] == ",":
                node.prefix = Prefix.ContDesc
        elif line.startswith("-~==~-"):
            node.prefix = Prefix.SectBreak
        elif line.startswith("-"):
            node.prefix = Prefix.PlainNode
        else:
            raise ValueError(f"Unable to tokenise line: '{line}'")
        # If this succeeded without raising an error, make contents
    return node


class BlockDoc:
    """
    Document formed by a list of one or more `NodeBlock` elements,
    created upon reading file lines (newlines will be stripped).
    """

    def __init__(self, lines):
        self._parselines(lines)

    def _add_nodeblock(self, lines):
        self.blocks.append(NodeBlock(lines))

    def _parselines(self, doc_lines):
        doc_lines = [l.rstrip("\n") for l in doc_lines]
        self.blocks = []
        current_line_block = []
        for l in doc_lines:
            if l == "" and current_line_block:
                self._add_nodeblock(current_line_block)
                current_line_block = []
            else:
                current_line_block.append(l)
        if current_line_block:
            self._add_nodeblock(current_line_block)

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        self._blocks = blocks

    @property
    def n_blocks(self):
        return len(self.blocks)

    def __repr__(self):
        s = "s" if (self.n_blocks != 1) else ""
        return f"Document of {self.n_blocks} block{s}"

class NodeBlock:
    def __init__(self, block_lines):
        self._nodes = []  # private property
        self.parse_lines(block_lines)  # populate nodes property

    @property
    def nodes(self):
        return self._nodes

    def add_node(self, node):
        self._nodes.append(node)

    @property
    def nodecount(self):
        return len(self.nodes)

    def __repr__(self):
        return f"Block of {self.nodecount} nodes"

    def parse_lines(self, block_lines):
        parsed = []
        for l in block_lines:
            n = tokenise_line(l, seen=parsed)
            parsed.append(n)
        # Since preceding lines' nodes are modified in the processing
        # of subsequent lines, only add nodes to block after finishing.
        for node in parsed:
            self.add_node(node)
        return


class Node:
    """
    Provide a simple string-repr while storing the Prefix and Suffix
    as properties (intervening `contents` is just a string for now).
    """

    def __init__(self, prefix=None, contents=None, suffix=None):
        self.prefix = prefix
        self.contents = contents
        self.suffix = suffix

    def __repr__(self):
        pre = self.prefix.str if self.prefix else ""
        con = self.contents if self.contents else ""
        suf = self.suffix.str if self.suffix else ""
        return f"{pre}{con}{suf}"

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, p):
        if hasattr(self, "_prefix"):
            # modifying an already set prefix so must also modify `self.contents`
            ex_prefix = self.prefix
            if ex_prefix:
                assert self.contents, "Tried to change prefix on contents-less Node"
                self.contents = ex_prefix.str + self.contents  # reconstitute
            if p:
                self.contents = self.contents[len(p.str) :]
        if p:
            assert isinstance(p, Prefix)  # must be either `None` or `Prefix` Enum
        self._prefix = p

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, c):
        self._contents = c

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, s):
        if hasattr(self, "_suffix"):
            # modifying an already set suffix so must also modify `self.contents`
            ex_suffix = self.suffix
            if ex_suffix:
                assert self.contents, "Tried to change suffix on content-less Node"
                self.contents = self.contents + ex_suffix.str
            if s:
                self.contents = self.contents[: -len(s.str)]
        if s:
            assert isinstance(s, Suffix)  # must be either `None` or `Suffix` Enum
        self._suffix = s


class Affix(Enum):
    """
    Affixes following the MMD 'lever' format specification.
    """

    @classmethod
    def name_from_token(cls, tok):
        return cls.tok2name_dict.get(tok)

    @classmethod
    def token_from_name(cls, name):
        return cls.name2tok_dict.get(name)

    @classproperty
    def tok2name_dict(cls):
        d = {v.value[0]: v.name for v in list(cls.__members__.values())}
        return d

    @classproperty
    def name2tok_dict(cls):
        d = {v.name: v.value[0] for v in list(cls.__members__.values())}
        return d

    @property
    def str(self):
        return self.value[0]


class Prefix(Affix):
    """
    Prefixes following the MMD 'lever' format specification. Capital
    letters indicate token symbols [A to F, as well as G ('gap')].
    Note that no prefix is given for a blank line and a section break
    spans the entire line (it is treated as a terminating prefix).
    """

    PlainNode = ("-",)  # A or Cb [if line ends with colon and precedes C"
    FollowOn = ("-,",)  # Ac
    InitList = ("-:",)  # B [default: indicating a list] or Cr [if after C]
    ContList = ("-,:",)  # Bc
    Question = ("-?",)  # C
    ContQuestion = ("-,?",)  # Cc
    Descent = ("-..",)  # D
    ContDesc = ("-.,",)  # Dc
    Ascent = ("-,,",)  # Du
    Therefore = ("-:.",)  # E
    Because = ("-:'",)  # F
    SectBreak = ("-~==~-",)  # G


class Suffix(Affix):
    """
    Suffixes following the MMD 'lever' format specification'. Capital
    letters indicate token symbols [backwards from Z].
    """

    InitList = ":"
