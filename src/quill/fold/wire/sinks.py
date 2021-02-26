from pathlib import Path
from enum import Enum
from .html_page_util import HtmlDoc
from ...scan.io import mmd
from sys import stderr

__all__ = ["QADocSink", "DocSink"]

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
        return Path(self.src_file).stem # i.e. strip .mmd file extension

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

class RadioTranscriptDocSink:
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
        return Path(self.src_file).stem # i.e. strip .mmd file extension

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
    roundtable = QADocSink # TODO: change
    radio_transcript = RadioTranscriptDocSink
