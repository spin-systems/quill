from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

__all__ = ["AuditBuilder", "Auditer"]


@dataclass
class AuditBuilder:
    active: bool
    auditer: Auditer | None

    @classmethod
    def from_path(cls, active: bool, path: Path):
        return cls(active=active, auditer=Auditer.from_path(path))


@dataclass
class Auditer:
    """
    We only want to render things that are either:
    - not in the prior audit list (meaning they are newly created)
    - in the prior audit list with a different input hash (meaning they changed)
    - in the prior audit list with a different output hash (meaning our audit got stale)

    We also want to remove anything from the audit list that isn't rendered i.e. when
    the input file is deleted, we want to remove its record too

    Therefore we make a new audit log, `new`, adding records for each rendered item,
    skipping renders when the input hash on record matches, (with one exception: if the
    file's template hash on record doesn't).
    """

    log: pd.DataFrame
    new: pd.DataFrame
    path: Path
    fields = "f_in f_up f_out h_in h_out".split()

    @classmethod
    def from_path(cls, path: Path):
        log = cls.read_audit(path)
        new = log.drop(log.index)
        return cls(log=log, new=new, path=path)

    @classmethod
    def read_audit(cls, path: Path) -> pd.DataFrame:
        assert path.exists(), f"No TSV file at {path}"
        return pd.read_csv(path, delimiter="\t", header=None, names=cls.fields)

    @staticmethod
    def checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128) -> str:
        h = hash_factory()
        with open(filename, "rb") as f:
            while chunk := f.read(chunk_num_blocks * h.block_size):
                h.update(chunk)
        return h.digest().hex()
