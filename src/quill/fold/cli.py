"""
Note: standup implemented for cut, but not for wire.
This could be added in future but the funcdef names would need to change
(cannot alias them, and are hardcoded in CI pipeline scripts, which would need to be
changed first: in fact the pipelines could use the entrypoints rather than -c flag)
"""

import defopt

from .cut.cutters import standup
from .cut.interface import CylConfig, StandupConfig

__all__ = ["run_defopt", "standup_cli", "cyl_cli"]


def run_defopt(config_cls: type[CylConfig] | type[StandupConfig]):
    config = defopt.run(config_cls, no_negated_flags=True)
    return standup(config)


def standup_cli() -> None:
    run_defopt(StandupConfig)


def cyl_cli() -> None:
    run_defopt(CylConfig)
