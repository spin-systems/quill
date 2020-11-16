from bs4 import Tag
from .html_util import CustomHtmlTag

__all__ = ["NavLinkList", "UlLinkList", "MetaTag"]

###### Utility classes for specific tags

class NavLinkList(CustomHtmlTag):
    def __init__(self, titles, links, nav_params={}, ul_params={}):
        super().__init__(name="nav", **nav_params)
        ul = UlLinkList(titles, links, ul_params=ul_params)
        self.append(ul)

class UlLinkList(CustomHtmlTag):
    def __init__(self, titles, links, ul_params={}):
        self.titles = titles
        self.links = links
        super().__init__(name="ul", **ul_params)
        li_tags = []
        for t,l in zip(self.titles, self.links):
            li_tag = Tag(name="li")
            a_tag = Tag(name="a", attrs={"href": l}) # coerces to string
            a_tag.append(f"{t}") # needs coercing to string
            li_tag.append(a_tag)
            self.append(li_tag)

class MetaTag(Tag):
    def __init__(self, attrs):
        super().__init__(name="meta", attrs=attrs, can_be_empty_element=True)
