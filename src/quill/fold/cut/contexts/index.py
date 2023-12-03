from __future__ import annotations

from ...auditing import AuditBuilder
from .helpers import audit_template, log_template

__all__ = ["index"]


@log_template
@audit_template
def index(template, audit_builder: AuditBuilder):
    """The home/front page (main subdomain index page)."""
    return {}
