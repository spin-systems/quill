"""
Note: standup implemented for cut, but not for wire.
This could be added in future but the funcdef names would need to change
(cannot alias them, and are hardcoded in CI pipeline scripts, which would need to be
changed first: in fact the pipelines could use the entrypoints rather than -c flag)
"""

import defopt

from .cut.cutters import standup as cut_standup
from .cut.interface import CylConfig, StandupConfig
from .git import source_manifest, stash_transfer_site_manifest
from .ns_util import ns
from .wire.wiring import standup as wire_standup

__all__ = ["run_defopt", "standup_cli", "cyl_cli"]


def run_defopt(config_cls: type[CylConfig] | type[StandupConfig]) -> None:
    config = defopt.run(config_cls, no_negated_flags=True)
    print(f"Namespace: {ns}")
    print(f"Loaded CLI config: {config!r}")
    if config.gitlab_ci:
        print("Sourcing repos from manifest")
        source_manifest()
    print("Creating fold.cut artifacts")
    cut_standup(config)
    if config.internal:
        print("Creating fold.wire artifacts")
        wire_standup(config)
    if config.gitlab_ci:
        print("Stashing and transferring site branches from manifest")
        stash_transfer_site_manifest()
    return


def standup_cli() -> None:
    run_defopt(StandupConfig)


def cyl_cli() -> None:
    run_defopt(CylConfig)
