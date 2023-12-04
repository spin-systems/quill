from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from ...auditing import AuditBuilder
from .helpers import log_template, skip_auditer
from .models import BaseContext

__all__ = ["base"]


@log_template
def base(template: Template, template_dir: Path, audit_builder: AuditBuilder):
    """A context providing the template date"""
    if skip_auditer(audit_builder, template, "base"):
        return {}
    else:
        return BaseContext.from_ctx(template, template_dir, audit_builder).model_dump()
