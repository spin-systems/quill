from os import walk
from itertools import chain
from configparser import ConfigParser
from pathlib import Path
from ..ns_util import ns, ns_path
from enum import Enum
from ...scan.io import mmd
from functools import partial

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
        return [x.relative_to(self.dir) for x in self.docs]

class QADocSink:
    def __init__(self, source_dir, sink_file):
        self.file = sink_file
        self.filepath = (source_dir / sink_file).resolve()

class DocSink(Enum):
    qa = QADocSink

class Wire:
    def __init__(self, filepath):
        self.source = mmd(filepath)
        self.source_dir = filepath.parent
        self.sinks = []
        for b in self.source.blocks:
            # TODO: add a lever parsing class rather than manually doing this
            d = dict([map(str.strip, n.contents.split("⠶")) for n in b.nodes])
            files = d.get("transmit").split(",")
            template = d.get("template")
            # Enum wrapper to template class: select the class from template string
            sink_func = getattr(DocSink, template).value
            # positional arg partial func: different files share same source directory
            pfunc = partial(sink_func, self.source_dir)
            templated_sinks = list(map(pfunc, files))
            self.sinks.extend(templated_sinks)

class WireEmitter(BaseEmitter):
    def __init__(self, directory, name):
        print(f"== WireEmitter: '{name}'==")
        self.dir = directory
        self.name = name
        self._procure_documents() # populate the docs property via wire files
        self._emit()

    def _procure_documents(self):
        walker = walk(self.dir)
        wire = "wire.mmt"
        dirs = [Path(p) for (p, _, filenames) in walker if wire in filenames]
        self.wires = [(p / wire) for p in dirs]
        self._Wires = [Wire(w) for w in self.wires]
        self.docs = list(chain.from_iterable([w.sinks for w in self._Wires]))

    def _emit(self):
        # put the files in the new directory
        for d in self.docs:
            print(d.file)


class Emitter(Enum):
    wire = WireEmitter
