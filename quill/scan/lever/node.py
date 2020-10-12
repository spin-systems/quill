from .tokens import Suffix, Prefix, tokenise_line

__all__ = ["Node"]

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
