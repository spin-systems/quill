from os import walk
from itertools import chain
from pathlib import Path
from enum import Enum
from ...scan.io import mmd
from functools import partial
from .transforms import basic_transform
from ..yaml_util import get_yaml_manifest
from ..ns_util import ns_path
from .....__share__ import alphanum2num_monthdict

__all__ = ["Emitter"]

class BaseEmitter:
    """
    The minimum viable task of an emitter is to take a directory of MMD documents
    and transform it into a corresponding HTML output.

    The first built on top of this is `WireEmitter`, which uses a `wire.mmt` file
    to specify which files in the directory will be emitted (not necessary if all
    will be).
    """
    @property
    def doc_subpaths(self):
        "Probably doesn't work/don't need (to be deleted...)"
        return [x.src_filepath.relative_to(self.dir) for x in self.docs]

class QADocSink:
    def __init__(self, date, src_dir, src_file):
        self.date = date
        self.src_file = src_file
        self.src_filepath = (src_dir / src_file).resolve()

    def transform(self):
        src = mmd(self.src_filepath)
        self.output = basic_transform(src)

    @property
    def target(self):
        return self.src_file.rstrip(".mmd") + ".html"

    def emit(self, target_dir):
        self.transform()
        # dumb approach, but do it for now
        date_subpath = Path(*self.date)
        emit_dir = target_dir / date_subpath
        if not emit_dir.exists():
            emit_dir.mkdir(parents=True)
        emit_path = emit_dir / self.target
        print(f"Emitting --> {emit_path}")
        with open(emit_path, "w") as f:
            f.write(self.output)

class DocSink(Enum):
    qa = QADocSink

def match_date_parts(path_parts):
    for i, p in enumerate(path_parts):
        if i == 0 or i >= len(path_parts) - 1:
            continue # skip first and last parts for indexing trios
        if p in alphanum2num_monthdict:
            p_pre, p_post = path_parts[i-1], path_parts[i+1]
            if p_pre.isnumeric() and p_post.isnumeric():
                numeric_month = str(alphanum2num_monthdict.get(p))
                return p_pre, numeric_month, p_post
    raise ValueError(f"No alphanumeric month-containing date found in '{path_parts}'")

class Wire:
    def __init__(self, filepath):
        self.date = match_date_parts(filepath.parts)
        self.source = mmd(filepath)
        self.source_dir = filepath.parent
        self.sinks = []
        for b in self.source.blocks:
            # TODO: add a lever parsing class rather than manually doing this
            d = dict([map(str.strip, n.contents.split("⠶")) for n in b.nodes])
            source_files = d.get("transmit").split(",")
            template = d.get("template")
            # Enum wrapper to template class: select the class from template string
            sink_func = getattr(DocSink, template).value
            # positional arg partial func: different files share same source directory
            pfunc = partial(sink_func, self.date, self.source_dir)
            templated_sinks = list(map(pfunc, source_files))
            self.sinks.extend(templated_sinks)

class WireEmitter(BaseEmitter):
    def __init__(self, directory, name):
        print(f"== WireEmitter: '{name}'==")
        self.dir = directory
        subdir = get_yaml_manifest("poll").pages.script.cfg.get("subdirectory") # site
        self.target_dir = (self.dir / "..").resolve() / subdir / "wire"
        self.name = name
        self._procure_documents() # populate the docs property via wire files
        self._trigger()

    def _procure_documents(self):
        walker = walk(self.dir)
        wire = "wire.mmt"
        dirs = [Path(p) for (p, _, filenames) in walker if wire in filenames]
        self.wires = [(p / wire) for p in dirs]
        self._Wires = [Wire(w) for w in self.wires]
        self.docs = list(chain.from_iterable([w.sinks for w in self._Wires]))

    def _trigger(self):
        # put the files in the new directory
        for d in self.docs:
            # write output to target in the target directory
            d.emit(self.target_dir)


class Emitter(Enum):
    wire = WireEmitter
