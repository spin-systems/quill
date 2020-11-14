from os import walk
from sys import stderr
from itertools import chain
from pathlib import Path
from enum import Enum
from ...scan.io import mmd
from functools import partial
from .transforms import HtmlDoc, HtmlPage
from ..yaml_util import get_yaml_manifest
from ..ns_util import ns_path
from .....__share__ import alphanum2num_monthdict
from bs4 import Tag

__all__ = ["Emitter"]

class UlLinkList(Tag):
    def __init__(self, titles, links):
        self.titles = titles
        self.links = links
        super().__init__(name="ul")
        li_tags = []
        for t,l in zip(self.titles, self.links):
            li_tag = Tag(name="li")
            a_tag = Tag(name="a", attrs={"href": l}) # coerces to string
            a_tag.append(f"{t}") # needs coercing to string
            li_tag.append(a_tag)
            self.append(li_tag)
    
    def as_str(self):
        return self.prettify()

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
    def __init__(self, date, src_dir, src_file, verbose=True):
        self._verbose = verbose
        self.date = date
        self.src_file = src_file
        self.src_filepath = (src_dir / src_file).resolve()

    def transform(self):
        src = mmd(self.src_filepath)
        listparseconfig={"listclass": "auto", "strict_list_breaks": False}
        src = mmd(self.src_filepath, listparseconfig)
        # the following was formerly wrapped by "basic_transform" function
        file_depth = 4 # len(["wire", "yy", "mm", "dd"])
        self.output = HtmlDoc(src, depth_from_root=file_depth).as_str() 

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
        if self._verbose:
            print(f"Emitting --> {emit_path}", file=stderr)
        with open(emit_path, "w") as f:
            f.write(self.output)
        return emit_path

class DocSink(Enum):
    qa = QADocSink
    speech = QADocSink # TODO: change
    slides = QADocSink # TODO: change

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
            # TODO: add sink verbosity control via partial named (not positional) arg
            pfunc = partial(sink_func, self.date, self.source_dir)
            templated_sinks = list(map(pfunc, source_files))
            self.sinks.extend(templated_sinks)

class WireEmitter(BaseEmitter):
    def __init__(self, directory, name, verbose=False):
        self._verbose = verbose
        if self._verbose:
            print(f"== WireEmitter: '{name}'==", file=stderr)
        self.dir = directory
        subdir = get_yaml_manifest("poll").pages.script.cfg.get("subdirectory") # site
        self.target_dir = (self.dir / "..").resolve() / subdir / "wire"
        self.name = name
        self._procure_documents() # populate the docs property via wire files
        self.emit_log = [] # populated for the first time upon trigger 
        self._trigger()
        if self._verbose:
            print("Emit log: \n  " + "\n  ".join([str(x) for x in self.emit_log]), file=stderr)
        self._index_emissions()

    def _procure_documents(self):
        walker = walk(self.dir)
        wire = "wire.mmt"
        dirs = [Path(p) for (p, _, filenames) in walker if wire in filenames]
        if self._verbose:
            print("TARGET DIR ::", self.target_dir, file=stderr)
            print("All input wire dirs:", file=stderr)
            for p in dirs:
                print("  " + str(p), file=stderr)
        self.wires = [(p / wire) for p in dirs]
        self._Wires = [Wire(w) for w in self.wires]
        self.docs = list(chain.from_iterable([w.sinks for w in self._Wires]))

    def _trigger(self):
        # put the files in the new directory
        emitted_paths = []
        for d in self.docs:
            # write output to target in the target directory
            emitted_path = d.emit(self.target_dir)
            emitted_paths.append(emitted_path)
        self.emit_log.extend(emitted_paths) # set as empty list in __init__

    def _index_emissions(self):
        all_emission_dirs = sorted(set([p.parent for p in self.emit_log]))
        if self._verbose:
            print("Emit dirs:\n  " + "\n  ".join([str(x) for x in all_emission_dirs]), file=stderr)
        rel_dirs = [d.relative_to(self.target_dir) for d in all_emission_dirs]
        print("All wire emitted dirs:\n  " + "\n  ".join([f"{d}" for d in rel_dirs]))
        all_subdirs = [[d] + [x for x in d.parents if x.parts] for d in rel_dirs]
        unique_subdirs = [] # didn't feel like using a set
        for l in all_subdirs:
            for d in l:
                if d in unique_subdirs:
                    continue
                unique_subdirs.append(d)
        print("unique subdirs: \n  " + "\n  ".join([f"{s}" for s in sorted(unique_subdirs)]))
        su_subdirs = sorted(unique_subdirs)
        top_level_subdirs = [d for d in sorted(unique_subdirs) if len(d.parts) == 1]
        self._index_emission_dir(Path("."), top_level_subdirs)
        for d in su_subdirs:
            self._index_emission_dir(d, unique_subdirs)

    def _index_emission_dir(self, e_dir, all_subdirs):
        f_name = "index.html"
        full_e_dir = self.target_dir / e_dir
        p = full_e_dir / f_name
        #assert not p.exists(), f"Houston we have an {f_name} at {full_e_dir}!"
        if len(e_dir.parts) == 0: # i.e. the top-level path "."
            files_to_log = []
        else:
            files_to_log = sorted([e for e in self.emit_log if e.parent == full_e_dir])
            names_to_log = [p.relative_to(full_e_dir) for p in files_to_log]
        print(f"  ⇢ index files: {e_dir}")
        #print(f"...for: {[str(x) for x in self.emit_log]}")
        if files_to_log:
            # i.e. if there are direct file descendants of the directory (not just subdirs)
            index_html_file = self.make_index_for_emitted_files(names_to_log)
            with open(p, "w") as f:
                n_f = len(files_to_log)
                depth = len(e_dir.parts) + 1 # wire / e_dir / index.html
                f_str = f"{n_f} file{'s' if n_f != 1 else ''}"
                print(f"    Writing index of {f_str} at {p}")
                f.write(index_html_file)
        else:
            if len(e_dir.parts) == 0: # i.e. the top-level path "."
                subdirs = all_subdirs
                depth = len(e_dir.parts) + 1 # wire / e_dir / index.html
                index_html_file = self.make_wire_index(subdirs)
            else:
                subdirs = [d.relative_to(e_dir) for d in all_subdirs if d.parent == e_dir]
                depth = len(e_dir.parts) + 1 # wire / e_dir / index.html
                index_html_file = self.make_index_for_intermediate_dir(subdirs, depth)
            with open(p, "w") as f:
                n_sd = len(subdirs)
                subdir_str = f"{n_sd} subdirector{'ies' if n_sd != 1 else 'y'}"
                print(f"    Writing index of {subdir_str} at {p}")
                f.write(index_html_file)
            return

    @staticmethod
    def make_index_for_emitted_files(files):
        ul = UlLinkList(titles=files, links=files)
        return HtmlPage(ul, 4).as_str()

    @staticmethod
    def make_index_for_intermediate_dir(subdirs, depth):
        ul = UlLinkList(titles=subdirs, links=subdirs)
        #return f"<html>\n{ul.as_str()}\n</html>"
        return HtmlPage(ul, depth).as_str()

    @staticmethod
    def make_wire_index(subdirs):
        # TODO: do this date conversion properly and for all yy/mm/dd parts
        subdirs_as_years = [f"20{y}" for y in subdirs]
        ul = UlLinkList(titles=subdirs_as_years, links=subdirs)
        return HtmlPage(ul, 1).as_str()


class Emitter(Enum):
    wire = WireEmitter
