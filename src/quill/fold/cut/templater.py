from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from staticjinja import Reloader, Site

from ...__share__ import Logger
from ..auditing import AuditBuilder
from .ctx import GLOBAL_CTX_COUNT
from .ctx_building import get_default_ctxs, get_post_ctxs
from .rules import no_render, render_md

__all__ = ["cut_templates"]

Log, Err = next((logger.Log, logger.Err) for logger in [Logger(__name__)])


@dataclass
class Cutter:
    template_dir: Path
    out_dir: Path
    audit_builder: AuditBuilder
    contexts: list[tuple[str, Callable]]
    mergecontexts: bool
    watch: bool

    def make_site(self, rules: list[tuple[str, Callable]]) -> Site:
        site = Site.make_site(
            contexts=self.contexts,
            mergecontexts=self.mergecontexts,
            searchpath=self.template_dir,
            outpath=self.out_dir,
            rules=rules,
        )
        return site

    def render(self, site: Site, restrict_templates: list[str]) -> bool:
        try:
            if restrict_templates:
                temp_it = [t for t in site.templates if t.name in restrict_templates]
                # Like using the wrapper `site.render` but replacing its templates iterator
                site.render_templates(temp_it)
                site.copy_static(site.static_names)
                if self.watch:
                    Reloader(site).watch()
            else:
                site.render(use_reloader=self.watch)
                temp_it = site.templates
        except BaseException as exc:
            Err("Failed to render site", exc_info=True)
            logging.error(exc, exc_info=True)
            Log(f"\nFAIL: {exc}\n")
            success = False
        else:
            success = True
        finally:
            Log(f"CTX COUNTS: {GLOBAL_CTX_COUNT}")
            return success

    def calculate_recheck(self) -> None:
        auditer = self.audit_builder.auditer
        log_precis = auditer.naive_recheck(self.template_dir)
        auditer.naive_recheck_diff(self.template_dir, log_precis=log_precis)
        return


def cut_templates(
    template_dir: Path,
    out_dir: Path,
    audit_builder: AuditBuilder,
    mergecontexts: bool = True,
    dry_run: bool = False,
    recheck: bool = False,
    watch: bool = False,
) -> bool:
    default_ctxs = get_default_ctxs(template_dir, audit_builder=audit_builder)
    post_ctxs = get_post_ctxs(template_dir, audit_builder=audit_builder)
    contexts = default_ctxs + post_ctxs
    cutter = Cutter(
        template_dir=template_dir,
        out_dir=out_dir,
        audit_builder=audit_builder,
        contexts=contexts,
        mergecontexts=mergecontexts,
        watch=watch,
    )
    auditer = cutter.audit_builder.auditer
    render_rules = [(r".*", no_render)] if dry_run else [(r".*\.md", render_md)]
    if recheck:
        cutter.calculate_recheck()
        f_diff = auditer.diff_store["f_diff"]
        f_no_diff = auditer.diff_store["f_no_diff"]
        if not f_diff:
            # Simulate the no delta state that was found by naive recheck
            auditer.new = auditer.log.copy()
            success = True
        else:
            # TODO: handle one or more diff files. Copy log to new then fix by overwrite
            # on_rules = [
            #     (filename, render_md)
            #     for filename in f_diff
            #     if Path(filename).suffix == ".md"
            #     # NB: HTML files not caught as they don't use custom rules (yet?)
            #     # so simply not overruling them lets them be (re)generated
            # ]
            # off_rules = [(filename, no_render) for filename in f_no_diff]
            # render_rules = on_rules + off_rules
            pass
    allow_site_render = not recheck or (recheck and any(f_diff))
    if allow_site_render:
        site = cutter.make_site(rules=render_rules)
        success = cutter.render(site, restrict_templates=f_diff if recheck else [])
    if recheck and f_diff:
        # auditer.new = auditer.log + the new row overwriting...
        additions = auditer.new.copy()
        auditer.new = auditer.log.copy()
        for diffed_f in additions.f_in:
            added_record = additions[additions.f_in == diffed_f].squeeze()
            auditer.new[auditer.new.f_in == diffed_f] = added_record
    return success


# TODO: run a 2nd pass? (Problem: md state is computed in rule not context, so can't
# compare after a dry run, would need to refactor into the md context...)
# if audit_builder.active and success:
#     breakpoint()
#     dep_set, arr_set, alt_list = audit_builder.auditer.delta_inputs
#     # TODO: would want to delete the files that departed
#     arrived_inputs = list(arr_set)
#     blocked_inputs = ...  # All files with no delta
#     blocked_rules = [(f"{blocked}", no_render) for blocked in blocked_inputs]
#     selective_render_rules = [*blocked_rules, *render_rules]
#     site = cutter.make_site(rules=selective_render_rules)
#     success = cutter.render(site)
