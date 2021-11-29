from stag.ecs import Path, Page, Metadata


_NO_TYPE = "_NO_TYPE"


def make_meta(*types, content=""):
    for t in types:
        if t is _NO_TYPE:
            yield Metadata()
        else:
            yield Metadata(type=t)


def make_pages(site, *metadatas):
    # not set to ease assertions
    for i, md in enumerate(metadatas):
        yield site.make_page(f"/{i}", metadata=md)


def test_page_filter_any(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages())
    assert filtered == set(site.pages[0:5])


def test_page_filter_none(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages(None))
    assert filtered == {site.pages[0]}


def test_page_filter_type(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages("page"))
    assert filtered == {site.pages[1], site.pages[2]}


def test_page_filter_unexisting_type(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages("someethingelse"))
    assert filtered == set()
