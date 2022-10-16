from __future__ import annotations

import csv
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from sys import stderr

import pandas as pd

__all__ = ["AuditBuilder", "Auditer"]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def log(msg, use_logger=False):
    if use_logger:
        logger.info(msg)
    else:
        print(msg, file=stderr)


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
        """Read TSV, replacing NaN with None for later equality comparison"""
        assert path.exists(), f"No TSV file at {path}"
        df = pd.read_csv(path, delimiter="\t", header=None, names=cls.fields)
        return df.where(df.notnull(), [None])

    @staticmethod
    def checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128) -> str:
        h = hash_factory()
        with open(filename, "rb") as f:
            while chunk := f.read(chunk_num_blocks * h.block_size):
                h.update(chunk)
        return h.digest().hex()

    @property
    def delta(self) -> bool:
        """Whether the new audit result has changed from the previous one."""
        return not self.log.equals(self.new)

    @property
    def delta_inputs(self) -> set[str]:
        log_input_files = set(self.log.f_in)
        new_input_files = set(self.new.f_in)
        departed = set(log_input_files) - set(new_input_files)
        arrived = set(new_input_files) - set(log_input_files)
        return departed, arrived

    def write_delta(self) -> None:
        if self.delta:
            dep, arr = self.delta_inputs
            log(f"Input file delta: {len(dep)} gone, {len(arr)} new")
            mod_diff = pd.merge(self.log, self.new, how="outer", indicator="how")
            mod_diff = mod_diff.where(mod_diff.notnull(), [None])
            mod_rows = mod_diff.loc[mod_diff["how"] != "both"]
            old_rows = mod_rows[mod_rows.how == "left_only"].drop(columns="how")
            new_rows = mod_rows[mod_rows.how == "right_only"].drop(columns="how")
            old_mod_rows = old_rows[~old_rows.f_in.isin(dep)]
            new_mod_rows = new_rows[~new_rows.f_in.isin(arr)]
            log(f"Mod: {len(old_mod_rows)} in log changed (to {len(new_mod_rows)})")
            log(f"Old: {old_mod_rows}")
            log(f"New: {new_mod_rows}")
            log(f"Writing delta to {self.path} ({len(self.new)} rows)")
            self.new.to_csv(self.path, sep="\t", header=False, index=False)
        else:
            row_match = f"same {len(self.new)} rows"
            log(f"No delta, not overwriting {self.path} ({row_match})")
