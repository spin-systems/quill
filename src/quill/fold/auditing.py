from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pandas as pd

__all__ = ["checksum", "read_audit"]


def checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128) -> str:
    h = hash_factory()
    with open(filename, "rb") as f:
        while chunk := f.read(chunk_num_blocks * h.block_size):
            h.update(chunk)
    return h.digest().hex()


def read_audit(tsv_path: Path) -> pd.DataFrame:
    assert tsv_path.exists(), f"No TSV file at {tsv_path}"
    fields = "f_in f_up f_out h_in h_out".split()
    audit = pd.read_csv(tsv_path, delimiter="\t", header=None, names=fields)
    return audit
