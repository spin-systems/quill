from __future__ import annotations

from pathlib import Path

import pandas as pd

from ...__share__ import Logger
from ..auditing import Auditer

__all__ = ["check_audit"]

Log = Logger(__name__).Log


def check_audit(
    template,
    template_dir: Path,
    auditer: Auditer,
    known_upstream: Path | None = None,  # TODO: this is not used?
) -> bool:
    """
    We only want to render (here we'll say "generate") things that are either:
    - not in the audit list (meaning they are newly created)
    - in the audit list with a different input hash (meaning they changed)

    We also want to remove anything from the audit list that isn't rendered i.e. when
    the input file is deleted, we want to remove its record too

    Therefore we will make a new audit log, adding records for each rendered item
    (enabling us to check after finishing if any that were on record are no longer).

    We will skip renders when the input hash on record matches, so long as the file's
    template hash on record also matches (which we track as the 'upstream' file).

    Where we can't specify the upstream dependency, for now we will assume that it has
    complex dependency, and always prefer to regenerate it. For example: some
    `index.html` files are generated based on the articles in a series and partial
    templates of footer content. Since there is not a single path we can check, we
    won't assume it's unchanged (always regenerate it), erring on the side of caution.
    """
    # TODO: use the template changelog idea
    # To avoid repeatedly checking template files, we will keep a dict of
    # these, and look up the result in the dict rather than re-check them.
    # template_changelog = {}
    template_p = Path(template.filename)
    template_subp = Path(template.name)
    Log(f"Checking audit log for {template.name}")
    f_in_log_record = auditer.lookup(template.name, field="f_in", old_log=True)
    input_sum = auditer.checksum(template_p)
    if f_in_log_record.empty:
        # There is no record of the file in the audit log
        Log(f"No record: {template.name}")
        generate_output = True
    else:
        # The file is recorded in the audit log: check for change
        Log(f"Found record: {template.name}")
        if input_sum == f_in_log_record.h_in:
            # It's identical: the input file itself has not changed since last audited
            f_up = f_in_log_record.f_up
            if pd.isnull(f_up):
                # don't assume absence of upstream dependency that may have changed
                generate_output = True
            else:
                Log(f"Checking audit log for {f_up} (upstream of {template.name})")
                f_up_log_record = auditer.lookup(f_up, field="f_in", old_log=True)
                upstream_p = template_dir / f_up
                # Regenerate if the upstream changed
                msg = f"Upstream is not in log f_in: {f_up}"
                f_up_preaudited = auditer.new.f_in.eq(f_up).any()
                assert f_up_preaudited, f"{msg} (did you forget to preaudit layouts?)"
                generate_output = auditer.checksum(upstream_p) != f_up_log_record.h_in
        else:
            # It's changed
            generate_output = True
    auditer.enter(f_in=template.name, h_in=input_sum)
    if not generate_output:
        Log(f"  ! Identified no regeneration: {template}")
    return generate_output
