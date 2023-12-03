from __future__ import annotations

from pathlib import Path

from ...auditing import AuditBuilder
from ..audit_checking import check_audit
from ..datetime_util import fmt_mtime
from .helpers import log_template, skip_auditer

__all__ = ["base"]


@log_template
def base(
    template,
    template_dir: Path,
    audit_builder: AuditBuilder,
):
    """A context providing the template date"""
    if skip_auditer(audit_builder, template, "base"):
        return {}
    generate = (
        check_audit(template, template_dir=template_dir, auditer=auditer)
        if audit_builder.active
        else True
    )
    return {
        "template_date": fmt_mtime(Path(template.filename)),
        "base_generate": generate,
        "audit_builder": audit_builder,
        "template_dir": template_dir,
    }
