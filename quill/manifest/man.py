from ..fold import ns_path as ss
from ..scan import mmd

__all__ = ["ssm"]

ssm_p = ss / "manifest.mmd"
ssm = mmd(ssm_p)
