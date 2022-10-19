from __future__ import annotations


__all__ = ["GLOBAL_CTX_COUNT", "update_ctx_count"]

GLOBAL_CTX_COUNT = {}

def update_ctx_count(name):
    global GLOBAL_CTX_COUNT
    GLOBAL_CTX_COUNT.setdefault(name, 0)
    GLOBAL_CTX_COUNT[name] += 1
    return
