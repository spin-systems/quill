from yaml import load, Loader
from .ns_util import ns_path, ns
from .site_yaml import SiteCI
from ..manifest.man import ssm

__all__ = ["yaml2dict", "yaml_manifests"]

def yaml2dict(yaml_path):
    with open(yaml_path, "r") as f:
        return load(f, Loader=Loader)

def yaml_manifests(as_dicts=True, yaml_filename=".gitlab-ci.yml"):
    """
    Clone repos as per the manifest (`qu.ssm`)
    """
    ssm.check_manifest()
    df = ssm.repos_df.loc[:,("domain", "local")]
    manifest_dict = {}
    for domain, local in df.values:
        if local:
            local_path = ns_path / domain
            yaml_path = local_path / yaml_filename
            d = yaml2dict(yaml_path)
            manifest_dict.update({domain: d})
        else:
            pass # do not touch if not local (for now)
    if as_dicts:
        return manifest_dict
    else:
        layout_dict = {d: SiteCI(y) for d,y in manifest_dict.items()}
        return layout_dict

# Can I read the description from the config file?
