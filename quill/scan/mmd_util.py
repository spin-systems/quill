from .lever import BlockDoc

class MMD:
    def __init__(self, mmd_lines):
        self.parse_doc(mmd_lines)

    def parse_doc(self, lines):
        self.doc = BlockDoc(lines)

    def __repr__(self):
        return f"Parsed MMD file ({self.doc})"
