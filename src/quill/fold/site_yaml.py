from enum import Enum
from parse import parse as fparse

def check_yaml(yaml_dict, keys):
    "Validate keys of the YAML dict for a GitLab Pages CI config."
    for k in keys:
        assert k in yaml_dict, f"YAML missing key: '{k}'"

class Stage(Enum):
    "There are multiple possible stages but I think GLP just uses 'deploy'."
    #Build = "build"
    #Test = "test"
    Deploy = "deploy"

class Cmd(Enum):
    """
    Fixed strings to validate against (as an enum so as to be immutable and named),
    representing commands in a build script.  The `Cmd.Cp` command is templated,
    using "{}" which will be parsed by `parse` from the package `parse`, described
    as 'the opposite of format()' i.e. like f-strings in reverse.
    """
    Mk = "mkdir .public"
    Cp = "cp -r {}* .public"
    Mv = "mv .public public"

class Script:
    """
    The script (list of commands) to run, relating to serving files from a
    single directory (which must be named 'public').
    """
    def __init__(self, cmd_list):
        self.cfg = {}
        self.parse(cmd_list)

    template = [Cmd.Mk, {"subdirectory": Cmd.Cp}, Cmd.Mv]

    def parse(self, commands):
        for i,c in enumerate(commands):
            t = self.template[i]
            if isinstance(t, dict):
                # overwrite t with the variable command and parse against the command
                [(custom_varname, t)] = t.items()
                configured_value = fparse(t.value, c)
                val = configured_value.fixed[0] if configured_value else None
                self.cfg.update({custom_varname: val})
            else:
                assert t.value == c

    def __repr__(self):
        if not (subdir := self.cfg.get("subdirectory")):
            subdir = ""
        return f"Script <{subdir}>"

class Artifacts:
    """
    Build artifacts means things not tracked by git to be attached,
    i.e. the 'public' directory created during the Pages build.
    """
    def __init__(self, yaml_dict):
        assert "paths" in yaml_dict, "No paths artifact"
        paths = ["public"]
        self.paths = paths
        assert yaml_dict.get("paths") == paths, f"No artifact {paths=}"

    def __repr__(self):
        cls = self.__class__.__name__
        paths = self.paths
        return f"{cls}: {paths=}"

class Only:
    "Only run on the master branch (or else specify which `branch`)"
    def __init__(self, yaml_entry, branch="master"):
        assert yaml_entry == [branch], f"No path artifact {branch}"
        self.branch = [branch]

    def __repr__(self):
        cls = self.__class__.__name__
        branch = self.branch
        return f"{cls}: {branch=}"

class PagesJob:
    "Required to build GitLab Pages: validates YAML and stores as object"
    def __init__(self, yaml_dict):
        check_yaml(yaml_dict, ["stage", "script", "artifacts", "only"])
        self.stage = Stage(yaml_dict.get("stage"))
        self.script = Script(yaml_dict.get("script"))
        self.artifacts = Artifacts(yaml_dict.get("artifacts"))
        self.only = Only(yaml_dict.get("only"))
    
    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}: {{{self.stage}, {self.script}, {self.artifacts}, {self.only}}}"

class SiteCI:
    "Representing (and validating) a `gitlab-ci.yml` config deployed to GitLab Pages."
    def __init__(self, yaml_dict):
        check_yaml(yaml_dict, ["pages"])
        self.pages = PagesJob(yaml_dict.get("pages"))

    @property
    def pages(self):
        return self._pages

    @pages.setter
    def pages(self, pages):
        self._pages = pages

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}: {self.pages}"
