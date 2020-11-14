from bs4 import BeautifulSoup, Tag
from pathlib import Path
from enum import Enum

__all__ = ["node_html_tag", "HtmlBlock", "HtmlDoc"]

def node_html_tag(node, line_no=None):
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
    if pre_name == "SectBreak":
        t = Tag(name="hr")
        # never has inner content
    else:
        # anything with inner content goes here
        if pre_name.startswith("Header"):
            # headers can't go in inline span elements
            html_tag_name = pre_name.replace("Header", "h")
            t = Tag(name=html_tag_name)
        else:
            t = Tag(name="span")
        t.append(inner)
        t.append(suf_span)
    # Then regardless of whether/not the node has inner content:
    cls_list = ["Node", f"pre_{pre_name}"]
    if node.suffix:
        cls_list.append(f"suf_{node.suffix.name}")
    attrs = {"class": " ".join(cls_list), "prefix": pre, "suffix": suf}
    t.attrs.update(attrs)
    if line_no is not None:
        t.attrs.update({"id": f"L{line_no}"})
    return t

class HtmlBlock:
    def __init__(self, block, lists):
        self.number = block.number
        self.start_line = block.start_line
        self.end_line = block.end_line
        self.nodes = block.nodes
        self.lists = lists

    def as_soup(self):
        line_range_dict = {"from": f"{self.start_line}", "to": f"{self.end_line}"}
        attrs = {"class": "NodeBlock", "id": f"nb{self.number}", **line_range_dict}
        block_div = Tag(name="div", attrs=attrs)
        # TODO do this properly after rewriting list parsing so end lines are accurate
        #list_starts = [l.all_nodes[0].start_line for l in self.lists]
        #list_ends = [l.all_nodes[-1].end_line for l in self.lists]
        for i, n in enumerate(self.nodes):
            html_node = node_html_tag(n, self.start_line + i)
            block_div.append(html_node)
        return block_div

class HtmlPage:
    def __init__(self, content, depth_from_root):
        self.preamble = "<!doctype html>\n"
        self.content = content
        self.depth = depth_from_root
        self.head = self.css_head()

    def as_str(self):
        soup = BeautifulSoup(features="html5lib")
        html = Tag(soup, name="html")
        html.append(self.head)
        body = Tag(name="body")
        body.append(self.content)
        html.append(body)
        return self.preamble + html.prettify()

    def css_head(self):
        head = Tag(name="head")
        #css_href = "../../../../styles.css"
        css_href = str(Path(*[".."] * self.depth) / "styles.css")
        attrs = {"rel": "stylesheet", "href": css_href}
        style = Tag(name="link", attrs=attrs, can_be_empty_element=True)
        head.append(style)
        return head

class HtmlDoc(HtmlPage):
    def __init__(self, doc, depth_from_root):
        self.preamble = "<!doctype html>\n"
        self.doc = doc
        self.depth = depth_from_root
        self.head = self.css_head()

    def as_str(self):
        soup = BeautifulSoup(features="html5lib")
        html = Tag(soup, name="html")
        html.append(self.head)
        body = Tag(name="body")
        article = Tag(name="article")
        unassigned_lists = self.doc.lists.copy()
        for b in self.doc.blocks:
            assignable_lists = []
            for l in unassigned_lists:
                first_list_line = l.all_nodes[0].line_no
                last_block_line = b.end_line
                if first_list_line < last_block_line:
                    # the list is in this block
                    assignable_lists.append(l)
                # do stuff with the assignable lists in this block
            block_html = HtmlBlock(b, assignable_lists).as_soup()
            article.append(block_html)
            for l in assignable_lists:
                unassigned_lists.pop(0) # pop only after iterating over
        body.append(article)
        html.append(body)
        return self.preamble + html.prettify()
