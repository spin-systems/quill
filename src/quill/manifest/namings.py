from ..scan.io import mmd
from ..fold import ns_path
from pandas import concat

__all__ = ["m", "alias_df"]

cfg = {"sep": "=", "labels": ["domain", "alias"]}
m = mmd(ns_path / "alias.mmd", listparseconfig=cfg)
#aliases = {l.header.contents: [n.contents for n in l.nodes] for l in m.lists}
alias_df = {l.header.contents: l.as_df() for l in m.lists}
for alias_ns in alias_df:
    alias_df.get(alias_ns).insert(0, "namespace", alias_ns)
alias_df = concat([alias_df.get(alias_ns) for alias_ns in alias_df]).reset_index().drop("index", 1)
