from __future__ import annotations

from functools import wraps
from typing import Callable

from jinja2 import Template

from ....__share__ import Logger
from ...auditing import AuditBuilder
from ..ctx import update_ctx_count

__all__ = ["log_template", "skip_auditer", "audit_template"]

Log = Logger(__name__).Log


def log_template(func: Callable):
    @wraps(func)
    def wrapper(template: Template, *args, **kwargs):
        Log(f"- Prepping {template} ({func.__name__})")
        update_ctx_count(name=func.__name__)
        return func(template, *args, **kwargs)

    return wrapper


def skip_auditer(
    audit_builder: AuditBuilder, template: Template, func_name: str
) -> bool:
    if audit_builder.active:
        auditer = audit_builder.auditer
        if auditer.recheck and auditer.is_no_diff(template):
            Log(f"  x Skipping ctx (known no diff): {template} ({func_name})")
            return True
    return False


def audit_template(func):
    @wraps(func)
    def wrapper(template, audit_builder, *args, **kwargs):
        if skip_auditer(audit_builder, template, func.__name__):
            return {}
        return func(template, audit_builder, *args, **kwargs)

    return wrapper
