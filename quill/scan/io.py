from .lever import NodeBlock

__all__ = ["mmd"]

def mmd(mmd):
    with open(mmd) as f:
        mmd_lines = f.readlines()
    block = NodeBlock(mmd_lines)
    return block
