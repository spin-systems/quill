"""
Note: standup implemented for cut, but not for wire.
This could be added in future but the funcdef names would need to change
(cannot alias them, and are hardcoded in CI pipeline scripts, which would need to be
changed first: in fact the pipelines could use the entrypoints rather than -c flag)
"""

import defopt

from .cut.cutters import cyl, standup

__all__ = ["standup_cli", "cyl_cli"]


def standup_cli():
    defopt.run(standup)


def cyl_cli():
    defopt.run(cyl)
