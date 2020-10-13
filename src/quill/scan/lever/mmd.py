from .parser import Doc

__all__ = ["MMD"]

class MMD:
    def __init__(self, mmd_lines, listparseconfig=None):
        self.doc = Doc(mmd_lines, listparseconfig=listparseconfig)

    def __repr__(self):
        return f"Parsed MMD file ({self.doc})"
