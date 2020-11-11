from configparser import ConfigParser
from pathlib import Path
from ..ns_util import ns, ns_path
from .emitters import Emitter

__all__ = ["standup"]

def standup():
    ini_fn = "emitters.ini"
    ini_dir = Path(__file__).parent
    c = ConfigParser()
    with open(ini_dir / ini_fn, "r") as f:
        c.read_file(f, ini_fn)
    emitters = []
    for s in c.sections():
        if s not in ns:
            continue # skip 'DEFAULT' section
        sect = c[s]
        ns_p = (ns_path / s)
        assert ns_p.exists() and ns_p.is_dir(), f"{ns_p} not found"
        for k, v in sect.items():
            print(f"{k}-{v}")
            directory = ns_p / k
            e = getattr(Emitter, v).value
            emitter = e(directory, k)
            emitters.append(emitter)
    return emitters
