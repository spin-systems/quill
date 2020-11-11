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
    for domain in c.sections():
        if domain not in ns:
            continue # skip 'DEFAULT' section
        sect = c[domain]
        ns_p = (ns_path / domain)
        assert ns_p.exists() and ns_p.is_dir(), f"{ns_p} not found"
        for name, emit_type in sect.items():
            print(f"{name}-{emit_type}")
            directory = ns_p / name
            e = getattr(Emitter, emit_type).value
            emitter = e(directory, name)
            emitters.append(emitter)
    return emitters
