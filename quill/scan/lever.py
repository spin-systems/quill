from enum import Enum
from ...__share__ import classproperty

__all__ = []

class Prefix(Enum):
    """
    Prefixes following the MMD 'lever' format specification. Capital
    letters indicate token symbols [A to F, as well as G ('gap')].
    Note that no prefix is given for a blank line.
    """
    PlainNode = "-", # A or Cb [if line ends with colon and precedes C"
    FollowOn = "-,", # Ac
    InitList = "-:", # B [default: indicating a list] or Cr [if after C]
    ContList = "-,:", # Bc
    Question = "-?", # C
    ContQuestion = "-,?", #Cc
    Descent = "-..", # D
    ContDesc = "-.,", # Dc
    Ascent = "-,,", # Du
    Therefore = "-:.", # E
    Because = "-:'", # F
    SectBreak = "-~==~-", # G

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
