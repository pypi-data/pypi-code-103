""""""

import webmention
import websub
from micropub import server
from understory import web
from understory.web import tx

from .. import content

app = web.application(
    __name__,
    prefix="posts",
    args={
        "channel": r".+",
        "entry": r".+",
    },
    model=server.posts_model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.m.pub = server.posts_model(tx.db)
    yield


@app.wrap
def linkify_head(handler, main_app):
    """."""
    yield
    if tx.request.uri.path == "":
        web.add_rel_links(micropub="/posts")


def route_unrouted(handler, app):  # TODO XXX ???
    """Handle channels."""
    for channel in tx.m.pub.get_channels():
        if channel["resource"]["url"][0] == f"/{tx.request.uri.path}":
            posts = tx.m.pub.get_posts_by_channel(channel["resource"]["uid"][0])
            web.header("Content-Type", "text/html")
            raise web.OK(app.view.channel(channel, posts))
    yield


@app.control("")
class MicropubEndpoint:
    """Your posts."""

    def get(self):
        """"""
        try:
            form = web.form("q")
        except web.BadRequest:
            return app.view.activity(
                tx.m.pub.get_channels(), tx.m.pub.get_media(), tx.m.pub.get_posts()
            )

        def generate_channels():
            return [
                {"name": r["name"][0], "uid": r["uid"][0]}
                for r in tx.m.pub.get_channels()
            ]

        # TODO XXX elif form.q == "channel":
        # TODO XXX     response = {"channels": generate_channels()}
        if form.q == "config":
            response = server.get_config()
        elif form.q == "source":
            response = {}
            if "search" in form:
                response = {
                    "items": [
                        {"url": [r["resource"]["url"]]}
                        for r in tx.m.pub.search(form.search)
                    ]
                }
            elif "url" in form:
                response = dict(tx.m.pub.read(form.url))
            else:
                pass  # TODO list all posts
        elif form.q == "category":
            response = {"categories": tx.m.pub.get_categories()}
        else:
            raise web.BadRequest(
                """unsupported query.
                                    check `q=config` for support."""
            )
        web.header("Content-Type", "application/json")
        return response

    def post(self):
        """"""
        # TODO check for bearer token or session cookie
        try:
            form = web.form("h")
        except web.BadRequest:
            try:
                resource = web.form()
            except AttributeError:  # FIXME fix web.form() raise Exc
                resource = tx.request.body._data
        else:
            h = form.pop("h")
            properties = {
                k.rstrip("[]"): (v if isinstance(v, list) else [v])
                for k, v in form.items()
            }
            resource = {"type": [f"h-{h}"], "properties": properties}
        try:
            action = resource.pop("action")
        except KeyError:
            permalink, mentions = tx.m.pub.create(
                resource["type"][0].partition("-")[2], **resource["properties"]
            )
            # web.header("Link", '</blat>; rel="shortlink"', add=True)
            # web.header("Link", '<https://twitter.com/angelogladding/status/'
            #                    '30493490238590234>; rel="syndication"', add=True)

            # XXX web.braid(permalink, ...)

            # TODO web.enqueue(webmention.send, permalink, mentions)
            web.enqueue(
                websub.publish,
                f"{tx.origin}/subscriptions",
                f"{tx.origin}",
                str(content.Homepage().get()),
            )
            raise web.Created("post created", permalink)
        if action == "update":
            url = resource.pop("url")
            tx.m.pub.update(url, **resource)
            return
        elif action == "delete":
            url = resource.pop("url")
            tx.m.pub.delete(url)
            return "deleted"
        elif action == "undelete":
            pass


@app.control("channels")
class Channels:
    """Your channels."""

    def get(self):
        """"""
        return app.view.channels(tx.m.pub.get_channels())


@app.control("channels/{channel}")
class Channel:
    """A single channel."""

    def get(self):
        """"""
        return app.view.channel(self.channel)


@app.control("syndication")
class Syndication:
    """Your syndication destinations."""

    def get(self):
        """"""
        return app.view.syndication()

    def post(self):
        """"""
        destinations = web.form()
        if "twitter_username" in destinations:
            un = destinations.twitter_username
            # TODO pw = destinations.twitter_password
            # TODO sign in
            user_photo = ""  # TODO doc.qS(f"a[href=/{un}/photo] img").src
            destination = {
                "uid": f"//twitter.com/{un}",
                "name": f"{un} on Twitter",
                "service": {
                    "name": "Twitter",
                    "url": "//twitter.com",
                    "photo": "//abs.twimg.com/favicons/" "twitter.ico",
                },
                "user": {"name": un, "url": f"//twitter.com/{un}", "photo": user_photo},
            }
            tx.db.insert("syndication", destination=destination)
        if "github_username" in destinations:
            un = destinations.github_username
            # TODO token = destinations.github_token
            # TODO check the token
            user_photo = ""  # TODO doc.qS("img.avatar-user.width-full").src
            destination = {
                "uid": f"//github.com/{un}",
                "name": f"{un} on GitHub",
                "service": {
                    "name": "GitHub",
                    "url": "//github.com",
                    "photo": "//github.githubassets.com/" "favicons/favicon.png",
                },
                "user": {"name": un, "url": f"//github.com/{un}", "photo": user_photo},
            }
            tx.db.insert("syndication", destination=destination)
