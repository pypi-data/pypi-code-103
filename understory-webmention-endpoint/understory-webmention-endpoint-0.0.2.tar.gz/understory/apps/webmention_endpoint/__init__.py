"""A Webmention receiver/sender for the Understory framework."""

# TODO https://indieweb.org/Salmention
# TODO https://indieweb.org/Vouch

import webmention
from understory import web
from understory.web import tx

app = web.application(
    __name__,
    prefix="mentions",
    args={"mention_id": r"\w+"},
    model=webmention.model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.webmention = webmention.model(tx.db)
    yield


@app.wrap
def linkify_head(handler, main_app):
    """Ensure receiver link is in head of current document."""
    yield
    if tx.request.uri.path in ("",):
        web.add_rel_links(webmention="/mentions")


@app.wrap
def track_referrers(handler, main_app):
    """Store the origin provided in any Referer request headers."""
    # TODO print(f"REFERER: {tx.request.headers.get('Referer')}")
    yield


@app.control(r"")
class Mentions:
    """."""

    def get(self):
        """Return a page of all mentions."""
        return app.view.index(
            tx.webmention.get_received_mentions(), tx.webmention.get_sent_mentions()
        )

    def post(self):
        """"""
        form = web.form("source", "target")
        web.enqueue(webmention.receive, form.source, form.target)
        raise web.Accepted("webmention received")


@app.control(r"received")
class ReceivedMentions:
    """."""

    def get(self):
        """Details of the webmention, with status information in mf2."""
        return app.view.received.index(
            tx.webmention.get_received_mention_by_id(self.mention_id)
        )


@app.control(r"received/{mention_id}")
class ReceivedMention:
    """."""

    def get(self):
        """Details of the webmention, with status information in mf2."""
        return app.view.received.mention(
            tx.webmention.get_received_mention_by_id(self.mention_id)
        )

    def post(self):
        """Details of the webmention."""
        raise web.Accepted("webmention received")
        # XXX f"{tx.host.name}/mentions/{mention_id}")


@app.control(r"sent")
class SentMentions:
    """."""

    def get(self):
        """Details of the webmention, with status information in mf2."""
        return app.view.sent.index()
