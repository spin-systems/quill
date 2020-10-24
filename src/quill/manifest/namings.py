from ..scan.io import mmd
from ..fold import ns_path
from pandas import concat

__all__ = ["m", "alias_df"]
pk = ["domain", "alias"] # `labels` to name df cols and `part_keys` for attr names
cfg = {"sep": "=", "headersep": True, "labels": pk, "part_keys": pk}
m = mmd(ns_path / "alias.mmd", listparseconfig=cfg)
#aliases = {l.header.contents: [n.contents for n in l.nodes] for l in m.lists}
alias_df = {l.header.alias if l.header.alias else l.header.domain: l.as_df(forbid_header=True) for l in m.lists}
for alias_ns in alias_df:
    alias_df.get(alias_ns).insert(0, "namespace", alias_ns)
alias_df = concat([alias_df.get(alias_ns) for alias_ns in alias_df]).reset_index().drop("index", 1)
