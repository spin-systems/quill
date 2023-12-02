from pydantic import BaseModel

from ..ns_util import ns

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
    """

    domains_list: list[str] = [*ns]
    incremental: bool = False
    no_render: bool = False
    recheck: bool = False
    watch: bool = False


class StandupConfig(SiteConfig):
    internal: bool = True


class CylConfig(SiteConfig):
    internal: bool = False
