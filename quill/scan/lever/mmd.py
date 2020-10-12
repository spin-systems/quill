from .parser import Doc

__all__ = ["MMD"]

class MMD:
    def __init__(self, mmd_lines):
        self.doc = Doc(mmd_lines)

    def __repr__(self):
        return f"Parsed MMD file ({self.doc})"
