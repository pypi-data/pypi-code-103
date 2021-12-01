"""
WebSub publisher and subscriber implementations.

> WebSub provides a common mechanism for communication between publishers
> of any kind of Web content and their subscribers, based on HTTP web hooks.
> Subscription requests are relayed through hubs, which validate and verify
> the request. Hubs then distribute new and updated content to subscribers
> when it becomes available. WebSub was previously known as PubSubHubbub. [0]

[0]: https://w3.org/TR/websub

"""

from understory import sql, web
from understory.web import tx

subscription_lease = 60 * 60 * 24 * 90
model = sql.model(
    __name__,
    received_subscriptions={  # others following you
        "received_subscription_id": "TEXT UNIQUE",
        "subscribed": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "topic_url": "TEXT UNIQUE",
        "callback_url": "TEXT",
    },
    sent_subscriptions={  # you following others
        "sent_subscription_id": "TEXT UNIQUE",
        "subscribed": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "topic_url": "TEXT UNIQUE",
        "callback_url": "TEXT UNIQUE",
        "verified": "INTEGER NOT NULL",
    },
    incoming_posts={"sent_subscription_id": "TEXT", "permalink": "TEXT"},
)


def publish(hub_url, topic_url, resource):
    """"""
    for subscription in get_received_subscriptions_by_topic(tx.db, topic_url):
        if subscription["topic_url"] != topic_url:
            continue
        web.post(
            subscription["callback_url"],
            headers={
                "Content-Type": "text/html",
                "Link": ",".join(
                    (
                        f'<{hub_url}>; rel="hub"',
                        f'<{topic_url}>; rel="self"',
                    )
                ),
            },
            data=resource,
        ).text


def subscribe(subscription_prefix, topic_url):
    """Send subscription request."""
    self_url = web.discover_link(topic_url, "self")
    hub = web.discover_link(topic_url, "hub")
    callback_url = add_sent_subscription(tx.db, subscription_prefix, str(self_url))
    web.post(
        hub,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "hub.mode": "subscribe",
            "hub.topic": str(self_url),
            "hub.callback": callback_url,
        },
    )


def unsubscribe(subscription_id):
    # TODO send unsub request
    remove_sent_subscription(tx.db, subscription_id)


def verify_received_subscription(topic_url, callback_url):
    """Verify subscription request and add follower to database."""
    challenge = web.nbrandom(32)
    response = web.get(
        callback_url,
        params={
            "hub.mode": "subscribe",
            "hub.topic": topic_url,
            "hub.challenge": challenge,
            "hub.lease_seconds": subscription_lease,
        },
    )
    if response.text != challenge:
        raise web.BadRequest(
            "subscription verification response does not match challenge"
        )
    add_received_subscription(tx.db, topic_url, callback_url)


@model.control
def add_sent_subscription(db, subscription_prefix, topic_url):
    while True:
        sent_subscription_id = web.nbrandom(5)
        callback_url = f"{subscription_prefix}/{sent_subscription_id}"
        try:
            db.insert(
                "sent_subscriptions",
                sent_subscription_id=sent_subscription_id,
                topic_url=topic_url,
                callback_url=callback_url,
                verified=0,
            )
        except db.IntegrityError:
            continue
        break
    return callback_url


@model.control
def verify_sent_subscription(db, topic_url, callback_url):
    with db.transaction as cur:
        cur.update(
            "sent_subscriptions",
            verified=1,
            where="topic_url = ? AND callback_url = ?",
            vals=[topic_url, callback_url],
        )


@model.control
def remove_sent_subscription(db, send_subscription_id):
    db.delete(
        "sent_subscriptions",
        where="sent_subscription_id = ?",
        vals=[send_subscription_id],
    )


@model.control
def get_sent_subscriptions(db):
    return db.select("sent_subscriptions")


@model.control
def get_sent_subscription_by_id(db, sent_subscription_id):
    return db.select(
        "sent_subscriptions",
        where="sent_subscription_id = ?",
        vals=[sent_subscription_id],
    )[0]


@model.control
def add_received_subscription(db, topic_url, callback_url):
    while True:
        received_subscription_id = web.nbrandom(5)
        try:
            db.insert(
                "received_subscriptions",
                received_subscription_id=received_subscription_id,
                topic_url=topic_url,
                callback_url=callback_url,
            )
        except db.IntegrityError:
            continue
        break


@model.control
def get_received_subscriptions(db):
    return db.select("received_subscriptions")


@model.control
def get_received_subscriptions_by_topic(db, topic_url):
    return db.select("received_subscriptions", where="topic_url = ?", vals=[topic_url])
