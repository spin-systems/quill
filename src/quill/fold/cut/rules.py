from __future__ import annotations

from pathlib import Path

import pandas as pd

from ...__share__ import Logger
from .ctx import update_ctx_count
from .name_config import LAYOUT_DIRNAME, LAYOUT_FILENAME, POST_DIRNAME

__all__ = ["no_render", "render_md"]

Log = Logger(__name__).Log


def no_render(site, template, **kwargs):
    Log(f"  - Usurped render for {template} (no_render)")
    update_ctx_count(name="RULE::no_render")
    pass


def render_md(site, template, **kwargs):
    """A rule that receives the union of context dicts as kwargs"""
    audit_builder = kwargs.pop("audit_builder")
    template_dir = kwargs.pop("template_dir")  # not used?
    base_generate_flag = kwargs.pop("base_generate")
    layout_filename = kwargs.pop("layout_filename", LAYOUT_FILENAME)
    upstream_p = Path(LAYOUT_DIRNAME) / layout_filename
    upstream = str(upstream_p)
    # TODO record f_in for the upstream, again no f_out
    if "/drafts/" in template.name:
        return
    Log(f"Rendering {template} (md)")
    update_ctx_count(name="RULE::render_md")
    # i.e. posts/post1.md -> build/posts/post1.html
    template_out_as = Path(template.name).relative_to(Path(POST_DIRNAME))
    out_parts = list(template_out_as.parts)
    is_index = template_out_as.stem == "index"
    is_multipart = len(out_parts) > 1
    if is_multipart:
        if is_index:
            out_parts.pop()  # Remove the index, giving it the parent dir as its path
        template_out_as = Path("-".join(out_parts))
    # URLs do not have to end with .html so do not add suffix other than for index file
    # Multipart indexes drop the index name but for suffix we still treat the same
    out_suffix = ".html" if (is_index and not is_multipart) else ""
    out_subp = template_out_as.with_suffix(out_suffix)
    out = site.outpath / out_subp
    # Compile and stream the result
    if audit_builder.active:
        auditer = audit_builder.auditer
        f_in_new_record = auditer.lookup(template.name, field="f_in", old_log=False)
        assert (
            not f_in_new_record.empty
        ), f"Pre-written {template.name} record not found"
        Log(f"Checking audit log for {upstream} (upstream of {template.name})")
        upstream_generate_flag = auditer.xref_delta(upstream, field="f_in", on="h_in")
        generate_flag = base_generate_flag and upstream_generate_flag
        # Continued as turns out the stream-dumped result is not written yet
        no_output_msg = f"Output {out_subp} (from {template.name}) does not exist"
        assert out.exists(), no_output_msg
        no_source_msg = f"{template.name} (source for {out_subp}) does not exist"
        assert Path(template.filename).exists(), no_source_msg
        old_h_out = auditer.lookup(template.name, field="f_in").h_out
        new_h_out = auditer.checksum(out)  # it's too soon! Hasn't changed yet
        new_record = auditer.make_record(
            f_in=template.name,
            f_up=upstream,
            f_out=str(out_subp),
            h_in=auditer.checksum(template.filename),
            h_out=None,  # new_h_out, # (do not need to store h_out)
        )
        # Overwrite row with this new_record
        auditer.new[auditer.new.f_in == template.name] = new_record.squeeze()
        # TODO: to finish, add another field storing the result of whichever flag most
        # appropriately indicates `generate_output` (in this case `base_generate_flag`)
        # and in this part overwrite it (alongside the entire row), giving a simple
        # readout of the decision made per file?
    write_stream_out = not audit_builder.active or generate_flag
    Log(f"   ~ {write_stream_out=}")
    if write_stream_out:
        site.get_template(upstream).stream(**kwargs).dump(str(out), encoding="utf-8")


# N.B. currently ensures a previous row exists and then overwrites it,
# but since that means it doesn't do anything, could skip writing earlier and
# just insert? Unclear in what instances you would ever need the first
# (without any info on output file or hash). Its purpose is to catch files like
# "index.html" (which are not caught by the regex for the render_md rule)


# TODO: write a pre-routine that does layout (problem is no context) - DONE
# - Could even keep these separate on the auditer, and after going through the
#   documents, drop any that aren't used for files... (Hmm, overicing it?)
