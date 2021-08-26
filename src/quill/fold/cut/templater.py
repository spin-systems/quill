from ..ns_util import ns, ns_path
from pathlib import Path
from datetime import datetime as dt
from staticjinja import Site
from functools import partial
import markdown
import frontmatter
import dateparser

__all__ = ["standup"]

markdowner = markdown.Markdown(output_format="html5")

OUT_DIRNAME = "site"
TEMPLATE_DIRNAME = "src"
POST_DIRNAME = "posts"

def standup(domains_list=None, verbose=True):
    domains_list = domains_list or [*ns]
    for domain in domains_list:
        ns_p = ns_path / domain
        if not ns_p.exists() and ns_p.is_dir():
            raise ValueError(f"{ns_p} not found")
        template_dir = ns_p / TEMPLATE_DIRNAME
        if template_dir.exists():
            site_dir = ns_p / OUT_DIRNAME
            post_dir = template_dir / POST_DIRNAME
            extra_ctxs = []
            if post_dir.exists():
                for a in post_dir.iterdir():
                    print(a)
                post_leaf_dir = Path(POST_DIRNAME)
                post_ctxs = [
                    (str(post_leaf_dir / a.name), article)
                    for a in post_dir.iterdir()
                ]
                extra_ctxs.extend(post_ctxs)
                extra_ctxs.extend(
                    [("index.html", partial(indexed_articles, dir_path=post_dir))]
                )
            cut_templates(template_dir=template_dir, out_dir=site_dir, contexts=extra_ctxs)
            print(f"Built {template_dir}")


def fmt_mtime(path_to_file):
    mtime = path_to_file.stat().st_mtime
    date = dt.fromtimestamp(mtime)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def base(template):
    print(f"Rendering {template} (base)")
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
    }


def index(template):
    print(f"Rendering {template} (index)")
    return {}


def indexed_articles(template, dir_path):
    "Sort articles by date"
    return {
        "articles": sorted(
            [
                article(a, is_path=True)
                for a in dir_path.iterdir()
                if not a.is_dir()  # not sub-directory
                if not a.name.startswith("_")  # not partial template
            ],
            key=lambda d: d["date"],
            reverse=True,
        )
    }


def article(template, is_path=False):
    print(f"Rendering {template} (article)")
    template_path = template if is_path else Path(template.filename)
    if template_path.suffix != ".md":
        raise ValueError("Metadata is not supported for non-markdown articles")
    md_content = frontmatter.load(template_path)
    metadata = md_content.metadata
    required_keys = {"title", "desc", "date"}
    if not all(k in metadata for k in required_keys):
        raise ValueError(f"{template=} missing one or more of {required_keys=}")
    return {"url": template_path.stem, "mtime": fmt_mtime(template_path), **metadata}


def md_context(template):
    print(f"Rendering {template} (md context)")
    # markdown_content = Path(template.filename).read_text()
    md_content = frontmatter.load(template.filename)
    return {"post_content_html": markdowner.convert(md_content.content)}


def render_md(site, template, **kwargs):
    print(f"Rendering {template} (md)")
    # i.e. posts/post1.md -> build/posts/post1.html
    template_out_as = Path(template.name).relative_to(Path(POST_DIRNAME))
    out = site.outpath / template_out_as.with_suffix(".html")
    # Compile and stream the result
    site.get_template("layouts/_post.html").stream(**kwargs).dump(
        str(out), encoding="utf-8"
    )


def cut_templates(template_dir, out_dir, contexts=None, mergecontexts=True):
    default_ctxs = [
        (r".*\.(html|md)$", base),
        ("index.html", index),
        (r".*\.md", md_context),
    ]
    custom_contexts = contexts or []
    contexts = default_ctxs + custom_contexts
    site = Site.make_site(
        contexts=contexts,
        mergecontexts=mergecontexts,
        searchpath=template_dir,
        outpath=out_dir,
        rules=[(r".*\.md", render_md)],
    )
    site.render()
