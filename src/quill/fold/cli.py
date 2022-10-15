"""
Note: standup implemented for cut, but not for wire.
This could be added in future but the funcdef names would need to change
(cannot alias them, and are hardcoded in CI pipeline scripts, which would need to be
changed first: in fact the pipelines could use the entrypoints rather than -c flag)
"""

import defopt

from .cut.templater import cyl, standup

__all__ = ["fold_cli"]


def fold_cli():
    defopt.run([standup, cyl])
