from pydantic import BaseModel

__all__ = ["StandupConfig"]


class SiteConfig(BaseModel):
    """
    Configure input filtering and output display.

      :param internal: Whether to build sites internal (ql) or external (cyl,
                       not including 'fold.wire') to the repo.
      :param domains_list: Names of the subdomains to build.
      :param incremental: compute MD5 checksums for each of the generated files.
      :param no_render: Dry run mode.
      :param recheck: Only regenerate files whose input checksum has changed since the last
                      incremental run.
      :param watch: Rebuild the domains continuously (incompatible with incremental/recheck).
      :param verbose: Whether to announce what tasks are being carried out.
      :param gitlab_ci: Source the manifest repos (i.e. git pull them) and then stash
                        the changes after building, switch to the www branch, pop the
                        stash and push the changes (i.e. publish the website content).
    """

    domains_list: list[str] | None = None
    incremental: bool = False
    no_render: bool = False
    recheck: bool = False
    watch: bool = False
    verbose: bool = False
    gitlab_ci: bool = False


class StandupConfig(SiteConfig):
    internal: bool = True


class CylConfig(SiteConfig):
    internal: bool = False
