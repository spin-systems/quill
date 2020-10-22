from subprocess import run
from .ns_util import ns_path, ns
from ..manifest.man import ssm
from sys import stderr

__all__ = ["clone", "source_manifest"] #, "update_manifest"]

def clone(url, as_name=None, wd=ns_path, update_man=True):
    command = ["git", "clone", url]
    if as_name:
        command.append(as_name)
    run(command, cwd=wd)
    ns.refresh()
    if update_man:
        ssm.check_manifest()
    return

def source_manifest():
    """
    Clone repos as per the manifest (`qu.ssm`)
    """
    df = ssm.repos_df.loc[:,("domain", "git_url")]
    for domain, url in df.values:
        if (ns_path / domain).exists():
            continue # simply do not touch for now
        try:
            clone(url, as_name=domain, update_man=False)
        except Exception as e:
            print(f"Failed on {url}: {e}", file=stderr)
    ssm.check_manifest()
    return

#def update_manifest():
#    ssm.repos_df["local"] = [domain in ns for domain in ssm.repos_df.domain]
#    return

# Can I read the description from the config file?
