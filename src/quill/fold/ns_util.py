from ....__share__ import qu_path
from configparser import ConfigParser
from .subdomain import parse_subdomain_url

__all__ = ["ns", "ns_path"]

def resolve_ns_path(qp=qu_path, ini_fn="spin.ini"):
    c = ConfigParser()
    with open(qp / ini_fn, "r") as f:
        c.read_file(f, ini_fn)
    rel_level = c.get("PARENT", "relative")
    dir_name = c.get("PARENT", "dir_name")
    ns_p = (qu_path / rel_level / dir_name).resolve()
    return ns_p

def read_ns(qp=qu_path, ini_fn="spin.ini"):
    ns_p = resolve_ns_path(qu_path, ini_fn)
    ns_subdirs = [d.parts[-1] for d in ns_p.iterdir() if d.is_dir()]
    ns = {k: parse_subdomain_url(ns_p, k) for k in ns_subdirs}
    return ns

class NameSpaceDict(dict):
    def __init__(self):
        self.refresh()

    def refresh(self):
        if self != (fresh := read_ns()):
            self.clear()
            self.update(fresh)

ns = NameSpaceDict() #NameSpace()
ns_path = resolve_ns_path()
