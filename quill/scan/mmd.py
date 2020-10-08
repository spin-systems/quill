# World's most basic parser: TODO rewrite as PEG properly

from .lever import Prefix

def determine_prefix(line, preceded=None):
    """
    Follow rules for prefix tagging here
    """
    # TODO use `lever.Prefix` enum
    if line == "":
        return None
    if preceded is None:
        ...
    elif "-:" in preceded:
        cont_list = "-,:"
        if line.startswith(CONT_LIST):
            return CONT_LIST
    return prefix

class Line(str):
    def __init__(self, l):
        self.raw = l
        self.prefix, self.text = self._splitonprefix(l)

    def __repr__(self):
        return self.raw

    @staticmethod
    def _splitonprefix(l):
        if l.startswith(
        return self.split(prefix, rest)
