__all__ = ["mmd"]

def mmd(mmd):
    with open(mmd) as f:
        mmd_lines = f.readlines()
    return mmd_lines
