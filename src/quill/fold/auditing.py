from __future__ import annotations

import csv
import hashlib
import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from sys import stderr

import pandas as pd

# Move this to same level to avoid descending into cut for general purpose Auditer?
from .cut.name_config import LAYOUT_DIRNAME

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
    def from_path(cls, active: bool, path: Path, recheck: bool):
        return cls(active=active, auditer=Auditer.from_path(path, recheck=recheck))


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
    recheck: bool
    fields = "f_in f_up f_out h_in h_out".split()
    diff_store = {}

    @classmethod
    def from_path(cls, path: Path, recheck: bool):
        log = cls.read_audit(path)
        new = log.drop(log.index)
        return cls(log=log, new=new, path=path, recheck=recheck)

    @classmethod
    def read_audit(cls, path: Path) -> pd.DataFrame:
        """Read TSV, replacing NaN with None for later equality comparison"""
        assert path.exists(), f"No TSV file at {path}"
        df = pd.read_csv(path, delimiter="\t", header=None, names=cls.fields)
        return df.where(df.notnull(), [None])

    def preaudit_layouts(self, build_dir: Path, layout_dirname=LAYOUT_DIRNAME):
        """
        Audit the layouts so that any changes can trigger regeneration on downstream
        templates that get built from those layouts.
        """
        layout_dir = Path(build_dir) / layout_dirname
        for layout_p in layout_dir.iterdir():
            layout_subp = layout_p.relative_to(build_dir)
            layout_name = str(layout_subp)
            f_in_log_rec = self.lookup(layout_name, field="f_in", old_log=True)
            self.enter(f_in=layout_name, h_in=self.checksum(layout_p))
            # NB layouts will never get generated as not target of any contexts

    @staticmethod
    def make_record(
        f_in=None, f_up=None, f_out=None, h_in=None, h_out=None
    ) -> pd.DataFrame:
        record = dict(f_in=f_in, f_up=f_up, f_out=f_out, h_in=h_in, h_out=h_out)
        record_df = pd.DataFrame.from_records([record])
        return record_df

    def enter(self, f_in=None, f_up=None, f_out=None, h_in=None, h_out=None) -> None:
        r = self.make_record(f_in=f_in, f_up=f_up, f_out=f_out, h_in=h_in, h_out=h_out)
        self.new = pd.concat([self.new, r], ignore_index=True)

    def xref_delta(
        self, value, *, field="f_in", on="h_in", strict: bool = True
    ) -> bool:
        """Do lookup on `field` and compare None and/or str values in the field `on`."""
        old = self.lookup(value, field=field, old_log=True, strict=strict)
        new = self.lookup(value, field=field, old_log=False, strict=strict)
        if sum([old.empty, new.empty]) > 0:
            delta = sum([old.empty, new.empty]) == 1
        else:
            cmp_vals = (old[on], new[on])
            null_valued = pd.isnull([cmp_vals])
            delta = (
                not null_valued.all() if null_valued.any() else str.__eq__(*cmp_vals)
            )
        return delta

    def lookup(
        self, value, *, field="f_in", old_log: bool = True, strict: bool = True
    ) -> pd.Series | pd.DataFrame:
        """
        Match exactly one row of the DataFrame and return it as a Series, or
        return an empty DataFrame with the same columns if no records match.
        If `strict` is True, raise an error if multiple rows match on `f_in`.
        """
        assert field in self.fields, f"{field=} not in {self.fields=}"
        log = self.log if old_log else self.new
        log_record = log[log[field] == value].squeeze()
        if field == "f_in" and strict:
            if log_record.ndim > 1 and not log_record.empty:
                self.multirow_corruption_error(value)
        return log_record

    @staticmethod
    def multirow_corruption_error(indexed_file):
        err_msg = f"multiple rows for the same input file {indexed_file}"
        raise ValueError(f"Corrupt audit log: {err_msg}")

    @staticmethod
    def checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128) -> str:
        h = hash_factory()
        with open(filename, "rb") as f:
            while chunk := f.read(chunk_num_blocks * h.block_size):
                h.update(chunk)
        return h.digest().hex()

    def checksum_entry(self, entry: pd.Series, template_dir: Path):
        return self.checksum(template_dir / entry.f_in)

    def prechecked_upstream_entry(self, entry: pd.Series, check_in: pd.DataFrame):
        if entry.f_up is None:
            return True
        else:
            record = check_in[check_in.f_in == entry.f_up].squeeze()
            msg = "Did not get 1 f_up row match (either 0 or 2+): failed to look up"
            assert record.ndim == 1, f"{msg} {entry.f_up} (upstream of {entry.f_in})"
            return record.h_eq
        # return self.checksum(template_dir / entry.f_in)

    def naive_recheck(self, template_dir: Path) -> pd.DataFrame:
        """
        Assume the pre-existing audit list is comprehensive: check those files,
        record any changes to overwrite the log (so this check is idempotent,
        but potentially makes the log an unreliable map of the territory).
        """
        log_precis = self.log[["f_in", "f_up", "h_in"]].copy()
        checksum_dir = partial(self.checksum_entry, template_dir=template_dir)
        log_precis["h_new"] = log_precis.apply(checksum_dir, 1)
        log_precis["h_eq"] = log_precis.h_in == log_precis.h_new
        check_upstream = partial(self.prechecked_upstream_entry, check_in=log_precis)
        log_precis["h_up_eq"] = log_precis.apply(check_upstream, 1)
        return log_precis

    def naive_recheck_diff(self, template_dir: Path, *, log_precis=None) -> None:
        if log_precis is None:
            log_precis = self.naive_recheck(template_dir=template_dir)
        no_delta_mask = log_precis[["h_eq", "h_up_eq"]].all(axis=1)
        delta_files = log_precis.f_in[~no_delta_mask].to_list()
        no_delta_files = log_precis.f_in[no_delta_mask].to_list()
        self.store_recheck_diff(f_diff=delta_files, f_no_diff=no_delta_files)

    def store_recheck_diff(self, f_diff: list[str], f_no_diff: list[str]) -> None:
        self.diff_store.update({"f_diff": f_diff, "f_no_diff": f_no_diff})

    def is_no_diff(self, template) -> bool:
        return template.name in self.diff_store["f_no_diff"]

    @property
    def any_recheck_diff(self) -> bool:
        return self.recheck and any(self.diff_store["f_diff"])

    @property
    def delta(self) -> bool:
        """Whether the new audit result has changed from the previous one."""
        return not self.log.equals(self.new)

    @property
    def delta_inputs(self) -> tuple[set[str], set[str], list[str]]:
        log_input_files = set(self.log.f_in)
        new_input_files = set(self.new.f_in)
        departed = set(log_input_files) - set(new_input_files)
        arrived = set(new_input_files) - set(log_input_files)
        alterations = self.alterations[1]
        altered = list(alterations.f_in)
        return departed, arrived, altered

    @property
    def alterations(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        files_in_common = pd.merge(self.log, self.new, on="f_in", how="inner")
        unaltered_mask = self.new.apply(tuple, 1).isin(self.log.apply(tuple, 1))
        unaltered, altered = self.new[unaltered_mask], self.new[~unaltered_mask]
        return unaltered, altered

    def write_delta(self) -> None:
        if self.delta:
            dep, arr, alt = self.delta_inputs
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
