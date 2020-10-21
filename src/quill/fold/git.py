from subprocess import run
from .ns_util import ns_path, ns
from ..manifest.man import ssm
from sys import stderr

__all__ = ["clone", "source_manifest"]

def clone(url, as_name=None, wd=ns_path):
    command = ["git", "clone", url]
    if as_name:
        command.append(as_name)
    run(command, cwd=wd)
    ns.refresh()
    return

def source_manifest(pull_existing=False):
    """
    Clone repos as per the manifest (`qu.ssm`)
    """
    df = ssm.repos_df.loc[:,("domain", "git_url")]
    if pull_existing:
        ... #TODO
    for domain, url in df.values:
        if (ns_path / domain).exists():
            continue # simply do not touch for now
        try:
            clone(url, as_name=domain)
        except Exception as e:
            print(f"Failed on {url}: {e}", file=stderr)
    ssm.repos_df["local"] = [domain in ns for domain in ssm.repos_df.domain]
    return

# Can I read the description from the config file?
