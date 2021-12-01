"""A WebSub publisher/subscriber for the Understory framework."""

import microformats
import websub
from understory import web
from understory.web import tx

app = web.application(
    __name__,
    prefix="subscriptions",
    args={"subscription_id": r".+"},
    model=websub.model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.websub = websub.model(tx.db)
    yield


@app.wrap
def linkify_head(handler, main_app):
    """Ensure hub and topic links are in head of current document."""
    # TODO limit to subscribables
    yield
    if tx.request.uri.path in ("",):
        web.add_rel_links(hub="/subscriptions")
        web.add_rel_links(self=f"/{tx.request.uri.path}")


@app.control(r"")
class Hub:
    """."""

    def get(self):
        return app.view.hub(
            tx.websub.get_sent_subscriptions(), tx.websub.get_received_subscriptions()
        )

    def post(self):
        try:
            topic_url = web.form("topic_url").topic_url
        except web.BadRequest:
            pass
        else:
            web.enqueue(websub.subscribe, f"{tx.origin}/subscriptions/sent", topic_url)
            return app.view.sent.subscription_requested()
        mode = web.form("hub.mode")["hub.mode"]
        if mode != "subscribe":
            raise web.BadRequest(
                'hub only supports subscription; `hub.mode` must be "subscribe"'
            )
        form = web.form("hub.topic", "hub.callback")
        # TODO raise web.BadRequest("topic not found")
        web.enqueue(
            websub.verify_received_subscription, form["hub.topic"], form["hub.callback"]
        )
        raise web.Accepted("subscription request accepted")


@app.control(r"sent/{subscription_id}")
class SentSubscription:
    """."""

    def get(self):
        """Confirm subscription request."""
        try:
            action = web.form("action").action
        except web.BadRequest:
            pass
        else:
            if action == "unsubscribe":
                web.enqueue(websub.unsubscribe, self.subscription_id)
                return "unsubscribed"
            raise web.BadRequest("action must be `unsubscribe`")
        try:
            form = web.form(
                "hub.mode", "hub.topic", "hub.challenge", "hub.lease_seconds"
            )
        except web.BadRequest:
            pass
        else:
            tx.websub.verify_sent_subscription(
                form["hub.topic"],
                f"{tx.origin}/subscriptions/sent/{self.subscription_id}",
            )
            # TODO verify the subscription
            return form["hub.challenge"]
        return "sent sub"

    def post(self):
        """Check feed for updates (or store the fat ping)."""
        feed = microformats.parse(tx.request.body._data)
        for entry in microformats.interpret_feed(feed, "http://google.com")["entries"]:
            print(entry)
        return ""


@app.control(r"received/{subscription_id}")
class ReceivedSubscription:
    """."""

    def get(self):
        return app.view.sent.subscription(
            tx.websub.get_sent_subscription_by_id(self.subscription_id)
        )
