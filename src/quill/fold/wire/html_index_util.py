from bs4 import Tag
from .html_page_util import HtmlPage
from .html_util import Attrs, PartialAttrs
from .html_elem_util import NavLinkList

__all__ = ["BaseIndexPage", "IndexNav", "IndexUl", "EmittedIndex", "IntermedDirIndex", "WireIndex"]

class BaseIndexPage(HtmlPage):
    def __init__(self, nav, depth, head_params={}):
        self._nav_tag = nav
        super().__init__(self._index_content, depth, head_params)

    @property
    def _default_css_param(self):
        "Overrides HtmlPage property method of the same name, setting head styles"
        return ["styles", "index"]

    @property
    def head_params(self):
        return self._head_params

    @head_params.setter
    def head_params(self, params):
        self._head_params = params

    @property
    def _index_content(self):
        if hasattr(self, "_nav_header"):
            return [self._nav_header, self._nav_tag]
        else:
            return self._nav_tag

class IndexNav(PartialAttrs):
    def __init__(self, attrs):
        self.default_attrs = {"class": "index"}
        super().__init__(attrs)

class IndexUl(PartialAttrs):
    def __init__(self, attrs):
        #self.default_attrs = {}
        super().__init__(attrs)

class EmittedIndex(BaseIndexPage):
    def __init__(self, files, depth=4, head_params={}):
        self.head_params = head_params
        nav_params = IndexNav({"id": "file_index"})
        ul_params = IndexUl({"id": "files"})
        nav = NavLinkList(files, files, nav_params, ul_params)
        nh_attrs = Attrs({"id": "nav_header", "class": "breadcrumbs"})
        self._nav_header = Tag(name="h3", **nh_attrs)
        self._nav_header.string = "file_beep_boop" # breadcrumbs go here
        super().__init__(nav, depth)

class IntermedDirIndex(BaseIndexPage):
    def __init__(self, subdirs, depth, head_params={}):
        self.head_params = head_params
        nav_params = IndexNav({"id": "mid_index"})
        ul_params = IndexUl({"id": "index", "class": f"lvl_{depth}"})
        nav = NavLinkList(subdirs, subdirs, nav_params, ul_params)
        nh_attrs = Attrs({"id": "nav_header", "class": "breadcrumbs"})
        self._nav_header = Tag(name="h3", **nh_attrs)
        self._nav_header.string = "dir_beep_boop" # breadcrumbs go here
        super().__init__(nav, depth)

class WireIndex(BaseIndexPage):
    def __init__(self, subdirs, depth=1, head_params={}):
        self.head_params = head_params
        nav_params = IndexNav({"id": "wire_index"})
        ul_params = Attrs({"id": "wires"})
        subdirs_as_years = [f"20{y}" for y in subdirs]
        nav = NavLinkList(subdirs_as_years, subdirs, nav_params, ul_params)
        nh_attrs = Attrs({"id": "nav_header"})
        self._nav_header = Tag(name="h3", **nh_attrs)
        self._nav_header.string = "wire"
        super().__init__(nav, depth)
