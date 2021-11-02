from . import cut
from .ns_util import ns_path, ns, pre_existing_ns_p
from ..manifest.man import ssm
from sys import stderr
from git import Repo
from itertools import starmap
from subprocess import run
from shutil import rmtree
from os import utime
from pathlib import Path

__all__ = [
    "clone",
    "source_manifest",
    "GitNews",
    "preprocess_domains_list",
    "remote_push_manifest",
    "remote_pull_manifest",
    "stash_transfer_site_manifest",
]


def clone(url, as_name, wd=ns_path, update_man=True, use_git_mtime=False):
    """
    Clone a repo from ``url`` giving it the name ``as_name``. If ``use_git_mtime`` is
    ``True``, then modify the access and modified timestamps (atime and mtime) of all
    files in the git repo's working tree to be the most recent commit in the git log.
    """
    clone_path = wd / as_name
    repo = Repo.clone_from(url, to_path=clone_path)
    ns.refresh()
    if use_git_mtime:
        for n in repo.tree().list_traverse():
            filepath = clone_path / n.path
            unixtime = repo.git.log(
                "-1", "--format='%at'", "--", n.path
            ).strip("'")
            if not unixtime.isnumeric():
                raise ValueError(
                    f"git log gave non-numeric timestamp {unixtime} for {n.path}"
                    f" during the cloning of {url}"
                )
            utime(filepath, times=(int(unixtime), int(unixtime)))
    if update_man:
        ssm.check_manifest()
    return


def source_manifest(use_git_mtime=True):
    """
    Clone repos as per the manifest (`qu.ssm`), checking out the last branch listed in
    the branches field [space-separated names] if distributed. If ``use_git_mtime`` is
    ``True`` (the default), then modify the mtime of the cloned files with the time of
    their last commit in the git log, rather than the one created during cloning (which
    would otherwise be the current date and time).
    """
    df = ssm.repos_df.loc[:, ("domain", "git_url", "branches")]
    for domain, url, branches in df.values:
        if (ns_path / domain).exists():
            continue  # simply do not touch for now
        try:
            clone(url, as_name=domain, update_man=False, use_git_mtime=use_git_mtime)
        except Exception as e:
            print(f"Failed on {url}: {e}", file=stderr)
    ssm.check_manifest()
    return


class GitNews:
    status_mapping = {
        "M": "Changed",
        "A": "Added",
        "D": "Deleted",
        "R": "Renamed",
        "C": "Copied",
        "U": "Updated",
    }

    def __init__(self, repo, abbreviate_at=2):
        """
        Given a repo object, generate the `git status --porcelain` output
        and parse it to give an overview of what changed.
        """
        self._news = repo.git.status("--porcelain")
        self.gnew = self._news.split("\n")
        self.status_lists = [*map(self.get_status, self.status_mapping)]
        self.abbreviate_at = abbreviate_at

    @property
    def status_labels(self):
        return [*self.status_mapping.values()]

    @property
    def all_reports(self):
        return [
            *starmap(self.report_status, zip(self.status_labels, self.status_lists))
        ]

    def __news_repr__(self):
        report = [". ".join(stats) for stats in self.all_reports if stats]
        return ". ".join(report)

    def get_status(self, letter_code):
        return [stat[3:] for stat in self.gnew if stat[0] == letter_code]

    def abbreviate_status(self, status):
        return [f"{len(status)} files"] if len(status) > self.abbreviate_at else status

    def report_status(self, action, status):
        "Returns e.g. 'Changed fileA.' or 'Changed 3 files.' as a string."
        status = self.abbreviate_status(status) if self.abbreviate_at else status
        return [f"{action} ".join(["", ", ".join(l)]) for l in [status] if status]


def preprocess_domains_list(specific_domains):
    if specific_domains is None:
        domains = ssm.repos_df.domain
    else:
        if type(specific_domains) is list:
            domains = specific_domains
        elif type(specific_domains) is str:
            domains = [specific_domains]
        else:
            raise TypeError(f"Unexpected type for {specific_domains=}")
    return domains


def remote_push_manifest(
    commit_msg=None, refspec=None, specific_domains=None, prebuild=True
):
    """
    Run `git add --all` on each repo in the manifest (`qu.ssm`),
    i.e. apex and all subdomains, then `git commit -m "..."`
    where `...` is replaced by `commit_msg` or auto-generated
    if no commit is available.
    """
    domains = preprocess_domains_list(specific_domains)
    for domain in domains:
        repo_dir = ns_path / domain
        if not repo_dir.exists():
            print(f"Skipping '{repo_dir=!s}' (doesn't exist)", file=stderr)
            continue  # simply do not touch for now
        repo = Repo(repo_dir)
        repo.git.add("--all")
        if not repo.is_dirty():
            print(f"Skipping '{repo_dir=!s}' (working tree clean)", file=stderr)
            continue  # repo has no changes to untracked files, skip it
        if prebuild:
            cut.standup(domains_list=[domain])
            repo.git.add("--all")
        repo_commit_msg = commit_msg
        if repo_commit_msg is None:
            news = GitNews(repo)
            repo_commit_msg = news.__news_repr__()
        if repo_commit_msg == "":
            msg = f"git repo stage added to at '{repo_dir=!s}'"
            raise ValueError("{msg} - aborting commit (empty commit message)")
        else:
            repo.git.commit("-m", repo_commit_msg)
            print(f"Commit [{repo_dir=!s}] ⠶ {repo_commit_msg}", file=stderr)
            origin = repo.remotes.origin
            origin.push(refspec=refspec)
            print(f"⇢ Pushing ⠶ {origin.name}", file=stderr)
    ssm.check_manifest()
    return


def remote_pull_manifest(specific_domains=None):
    """
    Run `git pull` on each repo in the manifest (`qu.ssm`),
    i.e. apex and all subdomains.

    No merge method is specified (unclear whether this will be necessary).

    See here if there are problems:
    https://stackoverflow.com/questions/36891470/how-to-pull-with-gitpython
    """
    domains = preprocess_domains_list(specific_domains)
    for domain in domains:
        print(f"Examining {domain}...", file=stderr)
        repo_dir = ns_path / domain
        if not repo_dir.exists():
            print(f"Skipping '{repo_dir=!s}' (doesn't exist)", file=stderr)
            continue  # simply do not touch for now
        repo = Repo(repo_dir)
        origin = repo.remotes.origin
        origin.pull()  # not checked if returned Pull object stores useful info
        print(f"⇢ Pulling ⠶ {origin.name}", file=stderr)
    ssm.check_manifest()
    return

def copy_static_assets(repo_dir, from_name="static", to_name="site", purge=False):
    static_dir = repo_dir / from_name
    site_dir = repo_dir / to_name
    if purge and site_dir.exists():
        rmtree(site_dir)
    site_dir.mkdir(exist_ok=not purge)
    clobber_flag = [] if purge else ["--no-clobber"]
    cp_cmd = ["cp", "-r", *clobber_flag, f"{static_dir!s}/.", f"{site_dir!s}"]
    if run(cp_cmd).returncode != 0:
        raise ValueError(f"Failed to copy {static_dir=} to {site_dir=}")


def stash_transfer_site_manifest(
    commit_msg=None,
    stash_pathspec="site/",
    checkout_branch="www",
    purge=True,
    specific_domains=None,
    reset_branch=False,
):
    """
    Stash [push] the ``stash_pathspec`` (default: "site/"), then ``git clean`` any
    changes and checkout the ``checkout_branch`` (default: "www"). Purge the stashed
    pathspec (if any files exist there) and then pop the stash to place the generated
    files there (i.e. delete anything that was there beforehand so that it's not merged,
    but completely overwritten, avoiding stale files being deployed). Lastly, add the
    stash pathspec to the git index before committing it (default ``commit_msg`` is
    ``None``: use an auto-generated commit message) and then pushing the commit to the
    ``checkout_branch``. If ``reset_branch`` is ``True`` (default: ``False``) then the
    original branch is checked out (it should be clean as the pathspec stashed from the
    original branch and pushed to the ``checkout_branch`` were the same).

    To be used after a site has been built (implicitly on the master branch).
    """
    domains = preprocess_domains_list(specific_domains)
    for domain in domains:
        repo_dir = ns_path / domain
        if not repo_dir.exists():
            print(f"Skipping '{repo_dir=!s}' (doesn't exist)", file=stderr)
            continue  # simply do not touch for now
        elif (repo_dir / "static").exists():
            copy_static_assets(repo_dir)
        repo = Repo(repo_dir)
        initial_repo_branch = repo.active_branch.name
        # Stash the desired changes (only in the given pathspec)
        stashed_msg = repo.git.stash("push", "-a", "--", stash_pathspec)
        if stashed_msg == "No local changes to save":
            print(domain, stashed_msg, "⠶ Skipping", file=stderr)
            continue
        else:
            print("Stashed changes for", domain, file=stderr)
        # Clean away any potentially undesired changes
        repo.git.clean("-fdx")
        repo.git.checkout(checkout_branch)
        if purge:
            paths_to_rm = stash_pathspec.split(" ")  # no spaces in file/dir names!
            for rm_path in paths_to_rm:
                rm_p = repo_dir / rm_path
                if rm_p.exists():
                    rmtree(rm_p) if rm_p.is_dir() else rm_p.unlink()
                else:
                    print(f"Skipping '{rm_path=!s}' (doesn't exist)", file=stderr)
        repo.git.stash("pop")
        repo.git.add(stash_pathspec)
        if not repo.is_dirty():
            print(f"Skipping '{repo_dir=!s}' (working tree clean)", file=stderr)
            continue  # repo has no changes to tracked pathspec files, skip it
        repo_commit_msg = commit_msg
        if repo_commit_msg is None:
            news = GitNews(repo)
            repo_commit_msg = news.__news_repr__()
        if repo_commit_msg == "":
            msg = f"git repo stage added to at '{repo_dir=!s}'"
            raise ValueError("{msg} - aborting commit (empty commit message)")
        else:
            repo.git.commit("-m", repo_commit_msg)
            print(f"Commit [{repo_dir=!s}] ⠶ {repo_commit_msg}", file=stderr)
            origin = repo.remotes.origin
            origin.push(refspec=checkout_branch)
            print(f"⇢ Pushing ⠶ {origin.name} ({checkout_branch})", file=stderr)
        if reset_branch:
            repo.git.checkout(initial_repo_branch)
    ssm.check_manifest()
    return
