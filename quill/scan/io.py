from .mmd_util import MMD

__all__ = ["mmd"]

def mmd(filepath):
    with open(filepath) as f:
        mmd_lines = f.readlines()
    m = MMD(mmd_lines)
    return m
