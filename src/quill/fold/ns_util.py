from configparser import ConfigParser
from pathlib import Path
from sys import stderr

from ..__share__ import ql_path
from .distrib_setup import seed_manifest, seed_ns_aliases, seed_routing_table
from .subdomain import parse_subdomain_url

__all__ = ["ns", "ns_path", "cyl_path"]


def resolve_ns_path(qp=ql_path, ini_fn="spin.ini"):
    c = ConfigParser()
    with open(qp / ini_fn, "r") as f:
        c.read_file(f, ini_fn)
    rel_level = c.get("PARENT", "relative")
    dir_name = c.get("PARENT", "dir_name")
    # Refers to seeding artifacts (aliases, routing table, git manifest)
    seed = bool(int(c.get("PARENT", "seed")))
    ### This part is all about standardising whether local or distributed
    home_spin = Path.home() / "spin"
    is_home_setup = (qp / rel_level).resolve() == home_spin
    ns_p = home_spin / dir_name
    pre_existing_ns_p = ns_p.exists()
    # if this is not set up in the home directory, probably been distributed
    # if you resolve the namespace path you'll only check if the library
    # "ss" has been installed, which on PyPi is a subtitles library
    # (Don't do this! Instead set up an installation in the home directory)
    if not pre_existing_ns_p:
        ns_p.mkdir(parents=True)
        if seed:
            seed_ns_aliases(ns_p)
            seed_routing_table(ns_p)
            seed_manifest(ns_p)
    return ns_p, pre_existing_ns_p


def read_ns(qp=ql_path, ini_fn="spin.ini"):
    ns_p, pre_existing_ns_p = resolve_ns_path(qp, ini_fn)
    ns_subdirs = [d.name for d in ns_p.iterdir() if d.is_dir()]
    ns = {k: parse_subdomain_url(ns_p, k) for k in ns_subdirs}
    return ns, pre_existing_ns_p


class NameSpaceDict(dict):
    def __init__(self):
        self.refresh()

    def refresh(self):
        fresh, pre_existing_ns_p = read_ns()
        if self != fresh:
            self.clear()
            self.update(fresh)


ns = NameSpaceDict()  # NameSpace()
ns_path, pre_existing_ns_p = resolve_ns_path()
cyl_path, pre_existing_cyl_p = resolve_ns_path(ini_fn="cyl.ini")
