from bs4 import BeautifulSoup, Tag
from enum import Enum

def node_html_tag(node):
    "Should this be in scan⠶lever"
    pre_name = node.prefix.name
    pre = node.prefix.str if node.prefix else ""
    con = node.contents if node.contents else ""
    suf = node.suffix.str if node.suffix else ""
    inner = con.strip()
    if suf != "":
        suf_span = Tag(name="span")
        suf_span.append(suf)
    else:
        suf_span = ""
    if pre_name.startswith("Header"):
        html_tag_name = pre_name.replace("Header", "h")
        t = Tag(name=html_tag_name)
    else:
        t = Tag(name="p", attrs={"prefix": pre, "suffix": suf})
        t.append(inner)
        t.append(suf_span)
    return t

class HtmlBlock:
    def __init__(self, block):
        self.nodes = block.nodes

    def as_soup(self):
        html_nodes = [node_html_tag(n) for n in self.nodes]
        block_div = Tag(name="div")
        for n in html_nodes:
            block_div.append(n)
        return block_div

class HtmlDoc:
    def __init__(self, doc):
        self.preamble = "<!doctype html>\n"
        self.doc = doc
        self.head = self.css_head()

    def as_str(self):
        soup = BeautifulSoup(features="html5lib")
        html = Tag(soup, name="html")
        html.append(self.head)
        body = Tag(name="body")
        article = Tag(name="article")
        for b in self.doc.blocks:
            block_html = HtmlBlock(b).as_soup()
            article.append(block_html)
        body.append(article)
        html.append(body)
        return self.preamble + html.prettify()

    @staticmethod
    def css_head():
        head = Tag(name="head")
        css_href = "../../../../styles.css"
        attrs = {"rel": "stylesheet", "href": css_href}
        style = Tag(name="link", attrs=attrs, can_be_empty_element=True)
        head.append(style)
        return head

def basic_transform(doc):
    """
    Simple transform of a MMD document to HTML (string).
    """
    html = HtmlDoc(doc)
    return html.as_str()
