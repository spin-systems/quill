from ..fold import ns_path as ss
from ..scan import mmd
from ..scan.lever.lists import SepBlockList

__all__ = ["ssm"]

ssm_p = ss / "manifest.mmd"
sep_parse_config = {"sep": ":", "headersep": True, "labels": None}
config_dict = {"listclass": SepBlockList, "listconfig": sep_parse_config}
ssm = mmd(ssm_p, listparseconfig=config_dict)

def parse_man_node(node, is_apex=False, host="gitlab.com"):
    """
    Parse the ['human-authored'] sub/domain name and ['slugged'] repo name prefix
    from the manifest (a list in MMD file format). May not need `is_apex` depending
    on how I use this function.
    """
    colsv = node.contents.split(":")
    assert len(colsv) == 2, f"Expected 2 colon-separated values, got {len(colsv)}"
    domain, ref = col_sep_val.split(":")
    ref = "git@{host}:qu-plot/qu-plot.gitlab.io.git"
    return domain, ref

def read_man(man=ssm):
    """
    Process a `DocList` in `.mmd` list format, i.e. with colon-sep. values,
    as `subdomain:group` [where group doubles as the repo name prefix for
    GitLab] beginning with the apex domain as a list header, and followed by
    subdomains to be applied to the apex domain).
    """
    apex = man.header
    # TODO finish me
