import markdown

from stag.ecs import Page, Path, Content


def add_md_file(site, text, metadata=None, parse=False):
    if metadata is None:
        metadata = {}

    config = site.config
    html = markdown.markdown(text) if parse else None
    return site.make_page(
        "/page",
        source=Path("page/index.md", site.config.content),
        metadata=metadata,
        input=Content("md", text),
        output=Content("html", html),
    )


def contents(path):
    with open(path) as file:
        return file.read().strip()
