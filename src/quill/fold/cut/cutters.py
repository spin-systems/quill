from __future__ import annotations

from ...__share__ import Logger
from ..auditing import AuditBuilder
from ..ns_util import cyl_path, ns, ns_path
from .name_config import OUT_DIRNAME, TEMPLATE_DIRNAME
from .templater import cut_templates

__all__ = ["cyl", "standup"]

Log = Logger(__name__).Log


def cyl(
    domains_list: list[str] | None = None,
    *,
    incremental: bool = False,
    no_render: bool = False,
    recheck: bool = False,
    watch: bool = False,
    verbose: bool = True,
):
    standup(
        domains_list=domains_list,
        internal=False,
        incremental=incremental,
        no_render=no_render,
        recheck=recheck,
        watch=watch,
        verbose=verbose,
    )


def standup(
    domains_list: list[str] | None = None,
    *,
    internal: bool = True,
    incremental: bool = False,
    no_render: bool = False,
    recheck: bool = False,
    watch: bool = False,
    verbose: bool = True,
):
    domains_list = domains_list or [*ns]
    for domain in domains_list:
        ns_in_p = ns_path / domain
        if not (ns_in_p.exists() and ns_in_p.is_dir()):
            raise ValueError(f"{ns_in_p} not found")
        # ns_in_p for input and ns_out_p for output (not necessarily same)
        ns_out_p = (ns_path if internal else cyl_path) / domain
        site_dir = ns_out_p / (OUT_DIRNAME if internal else ".")
        template_dir = ns_in_p / TEMPLATE_DIRNAME
        if template_dir.exists():
            if incremental:
                audit_p = ns_out_p.parent / f"{domain}.tsv"
                if not audit_p.exists():
                    audit_p.touch()
                builder = AuditBuilder.from_path(
                    active=True, path=audit_p, recheck=recheck
                )
                if not recheck:
                    builder.auditer.preaudit_layouts(build_dir=template_dir)
            else:
                builder = AuditBuilder(active=False, auditer=None)
            success = cut_templates(
                template_dir=template_dir,
                out_dir=site_dir,
                audit_builder=builder,
                dry_run=no_render,
                recheck=recheck,
                watch=watch,
            )
            if success:
                Log(f"Built {template_dir}")
                if builder.active:
                    builder.auditer.write_delta()
            else:
                Log(f"Failed to build {template_dir}")
        Log(f"\nDONE ⠶ {domain}\n")
        if incremental:
            pass  # breakpoint()


# To handle incremental builds, we will do 2 passes, one without doing any renders, and
# one which takes the results of the previous pass to inform what is rendered (switching
# off files with rules for each detected input file)...
