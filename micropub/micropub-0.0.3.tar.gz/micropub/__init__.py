"""
A library for writing [Micropub][0] servers and clients.

> The Micropub protocol is used to create, update and delete posts on
> one's own domain using third-party clients. Web apps and native apps
> (e.g. iPhone, Android) can use Micropub to post and edit articles,
> short notes, comments, likes, photos, events or other kinds of posts
> on your own website.

[0]: https://micropub.spec.indieweb.org

"""

from . import client, readability, server

__all__ = ["client", "server", "markdown_globals", "readability"]


def book(isbn):
    return (
        f"<span class=h-cite><strong class=p-name>Book Title</strong> "
        f"(<em class=p-isbn>{isbn}</em>)</span>"
    )


markdown_globals = {"book": book}
