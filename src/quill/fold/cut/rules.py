from __future__ import annotations

from pathlib import Path

import pandas as pd  # noqa: F401
from jinja2 import Template
from pydantic import BaseModel, Field, computed_field
from pydantic.types import FilePath

from ...__share__ import Logger
from ..auditing import AuditBuilder, Auditer
from .ctx import update_ctx_count
from .name_config import LAYOUT_DIRNAME, LAYOUT_FILENAME, POST_DIRNAME

__all__ = ["no_render", "render_md"]

Log = Logger(__name__).Log


def no_render(site, template, **kwargs):
    Log(f"  - Usurped render for {template} (no_render)")
    update_ctx_count(name="RULE::no_render")


class TemplateIO(BaseModel, arbitrary_types_allowed=True):
    template: Template
    template_dir: Path | None = None
    layout_filename: str = LAYOUT_FILENAME
    post_dir: Path = Path(POST_DIRNAME)  # in practice fixed (could be a ClassVar)

    @computed_field
    @property
    def _name(self) -> str:
        return self.template.name

    @computed_field
    @property
    def _upstream(self) -> str:
        return str(Path(LAYOUT_DIRNAME) / self.layout_filename)

    @computed_field
    @property
    def _template_path(self) -> Path:
        """The subpath (not a complete path) beneat the `post_dir`)"""
        return Path(self._name)

    @computed_field
    @property
    def _full_template_path(self) -> Path:
        """The subpath (not a complete path) beneat the `post_dir`)"""
        return Path(self.template.filename)

    @computed_field
    @property
    def is_index(self) -> bool:
        return self._template_path.stem == "index"

    @computed_field
    @property
    def is_multipart(self) -> bool:
        return len(self.template_out_rel.parts) > 1

    @computed_field
    @property
    def template_out_rel(self) -> Path:
        return self._template_path.relative_to(self.post_dir)

    @computed_field
    @property
    def slugged_rel_template(self) -> Path:
        """Remove the index, giving it the parent dir as its path"""
        rel_parts = self.template_out_rel.parts[: (-1 if self.is_index else None)]
        return Path("-".join(rel_parts))

    @computed_field
    @property
    def out_suffix(self) -> str:
        """
        URLs do not have to end with .html so do not add suffix other than for index
        """
        return ".html" if (self.is_index and not self.is_multipart) else ""

    @computed_field
    @property
    def template_out_as(self) -> Path:
        """Remove the index if multipart index."""
        return self.slugged_rel_template if self.is_multipart else self.template_out_rel

    @computed_field
    @property
    def out_subpath(self) -> Path:
        """
        Multipart indexes drop the index name but for suffix we still treat the same
        """
        return self.template_out_as.with_suffix(self.out_suffix)


class MDRender(TemplateIO):
    audit_builder: AuditBuilder | None = None
    base_generate: bool = False
    upstream: str = Field(validation_alias="_upstream")
    full_path: FilePath = Field(validation_alias="_full_template_path")
    # upstream: Path = Field(validation_alias="_upstream")

    @property
    def auditer(self) -> Auditer:
        return self.audit_builder.auditer

    @property
    def ok_to_generate(self) -> bool:
        """Mysterious comment: 'TODO record f_in for the upstream, again no f_out'."""
        upstream_generate_flag = self.auditer.xref_delta(
            self.upstream, field="f_in", on="h_in"
        )
        return self.base_generate and upstream_generate_flag

    @property
    def write_stream_out(self) -> bool:
        return not self.audit_builder.active or self.ok_to_generate

    @property
    def skipped(self) -> bool:
        """Don't render drafts (or insert any other exclusion logic here)."""
        return "drafts" in self.template_out_rel.parts

    @classmethod
    def from_fs_io(cls, **kwargs: dict) -> MDRender:
        return cls(**{**kwargs, **TemplateIO.model_validate(kwargs).model_dump()})

    def run_audit(self, output: Path) -> None:
        """
        Look up the template being built in the audit log, compare hash values of
        previous and current states, and create a new record.
        """
        f_in_new_record = self.auditer.lookup(self._name, field="f_in", old_log=False)
        assert not f_in_new_record.empty, f"Pre-written {self._name} record not found"
        Log(f"Checking audit log for {self.upstream} (upstream of {self._name})")
        # Continued as turns out the stream-dumped result is not written yet
        no_output_msg = f"Output {self.out_subpath} (from {self._name}) does not exist"
        assert output.exists(), no_output_msg
        no_source_msg = f"{self._name} (source for {self.out_subpath}) does not exist"
        assert Path(self.template.filename).exists(), no_source_msg
        # old_h_out = self.auditer.lookup(self._name, field="f_in").h_out
        # new_h_out = self.auditer.checksum(out)  # it's too soon! Hasn't changed yet
        new_record = self.auditer.make_record(
            f_in=self._name,
            f_up=self.upstream,
            f_out=str(self.out_subpath),
            h_in=self.auditer.checksum(self.template.filename),
            h_out=None,  # new_h_out, # (do not need to store h_out)
        )
        # Overwrite row with this new_record
        self.auditer.new[self.auditer.new.f_in == self._name] = new_record.squeeze()
        # TODO: to finish, add another field storing the result of whichever flag most
        # appropriately indicates `generate_output` (in this case `base_generate`)
        # and in this part overwrite it (alongside the entire row), giving a simple
        # readout of the decision made per file?


def render_md(site, template, **kwargs):
    """A rule that receives the union of context dicts as kwargs"""
    config = MDRender.from_fs_io(template=template, **kwargs)
    if config.skipped:
        Log(f"Skipping {config.template} (md)")
    else:
        Log(f"Rendering {config.template} (md)")
        update_ctx_count(name="RULE::render_md")
        output = site.outpath / config.out_subpath
        if config.audit_builder.active:
            config.run_audit(output=output)
        Log(f"   ~ {config.write_stream_out=}")
        if config.write_stream_out:
            # Compile and stream the result
            blueprint = site.get_template(config.upstream)
            blueprint.stream(**kwargs).dump(str(output), encoding="utf-8")


# N.B. currently ensures a previous row exists and then overwrites it,
# but since that means it doesn't do anything, could skip writing earlier and
# just insert? Unclear in what instances you would ever need the first
# (without any info on output file or hash). Its purpose is to catch files like
# "index.html" (which are not caught by the regex for the render_md rule)


# TODO: write a pre-routine that does layout (problem is no context) - DONE
# - Could even keep these separate on the auditer, and after going through the
#   documents, drop any that aren't used for files... (Hmm, overicing it?)
