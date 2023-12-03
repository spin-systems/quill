from __future__ import annotations

from ...__share__ import Logger
from ..auditing import AuditBuilder
from ..ns_util import cyl_path, ns, ns_path
from .interface import CylConfig, StandupConfig
from .name_config import OUT_DIRNAME, TEMPLATE_DIRNAME
from .templater import cut_templates

__all__ = ["standup"]

Log = Logger(__name__).Log


def standup(config: CylConfig | StandupConfig):
    if config.domains_list is None:
        config.domains_list = [*ns]
        print(f"Changed domains list to full list: {config.domains_list}")
    for domain in config.domains_list:
        ns_in_p = ns_path / domain
        if not (ns_in_p.exists() and ns_in_p.is_dir()):
            raise ValueError(f"{ns_in_p} not found")
        # ns_in_p for input and ns_out_p for output (not necessarily same)
        ns_out_p = (ns_path if config.internal else cyl_path) / domain
        site_dir = ns_out_p / (OUT_DIRNAME if config.internal else ".")
        template_dir = ns_in_p / TEMPLATE_DIRNAME
        if template_dir.exists():
            if config.incremental:
                audit_p = ns_out_p.parent / f"{domain}.tsv"
                if not audit_p.exists():
                    audit_p.touch()
                builder = AuditBuilder.from_path(
                    active=True, path=audit_p, recheck=config.recheck
                )
                if not config.recheck:
                    builder.auditer.preaudit_layouts(build_dir=template_dir)
            else:
                builder = AuditBuilder(active=False, auditer=None)
            success = cut_templates(
                template_dir=template_dir,
                out_dir=site_dir,
                audit_builder=builder,
                dry_run=config.no_render,
                recheck=config.recheck,
                watch=config.watch,
            )
            if success:
                Log(f"Built {template_dir}")
                if builder.active:
                    builder.auditer.write_delta()
            else:
                Log(f"Failed to build {template_dir}")
        Log(f"\nDONE ⠶ {domain}\n")
        if config.incremental:
            pass  # breakpoint()


# To handle incremental builds, we will do 2 passes, one without doing any renders, and
# one which takes the results of the previous pass to inform what is rendered (switching
# off files with rules for each detected input file)...
