from ...fold.ns_util import ns_path
from git import Repo

def _has_clean_wt(domain):
    """
    Helper function (TODO: move to a dedicated git module)
    """
    repo_dir = ns_path / domain
    assert repo_dir.exists(), f"{repo_dir=!s} in namespace but doesn't exist"
    return not Repo(repo_dir).is_dirty()
