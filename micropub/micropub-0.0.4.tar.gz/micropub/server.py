"""A Micropub server."""

import pathlib
import random

import pendulum
import vobject
# import webmention
import websub
from microformats import discover_post_type
from understory import sql, web
from understory.web import tx

__all__ = ["get_config"]


class PostNotFoundError(Exception):
    """Post could not be found."""


posts_model = sql.model(
    f"{__name__}.posts",
    resources={
        "permalink": "TEXT UNIQUE",
        "version": "TEXT UNIQUE",
        "resource": "JSON",
    },
    deleted_resources={
        "permalink": "TEXT UNIQUE",
        "version": "TEXT UNIQUE",
        "resource": "JSON",
    },
    syndication={"destination": "JSON NOT NULL"},
)
media_model = sql.model(
    f"{__name__}.media",
    media={"mid": "TEXT", "sha256": "TEXT UNIQUE", "size": "INTEGER"},
)

# TODO supported_types = {"RSVP": ["in-reply-to", "rsvp"]}


def get_config():
    """"""
    syndication_endpoints = []
    # TODO "channels": generate_channels()}
    return {
        "q": ["category", "contact", "source", "syndicate-to"],
        "media-endpoint": f"https://{tx.host.name}/pub/media",
        "syndicate-to": syndication_endpoints,
        "visibility": ["public", "unlisted", "private"],
        "timezone": "America/Los_Angeles",
    }


def generate_trailer():
    letterspace = "abcdefghijkmnopqrstuvwxyz23456789"
    trailer = "".join([random.choice(letterspace) for i in range(2)])
    if trailer in ("bs", "ok", "hi", "oz", "lb"):
        return generate_trailer()
    else:
        return trailer


@posts_model.control
def create(db, resource_type, **resource):
    """Create a resource."""
    for k, v in resource.items():
        if not isinstance(v, list):
            resource[k] = [v]
        flat_values = []
        for v in resource[k]:
            if isinstance(v, dict):
                if not ("html" in v or "datetime" in v):
                    v = dict(**v["properties"], type=[v["type"][0].removeprefix("h-")])
            flat_values.append(v)
        resource[k] = flat_values

    config = get_config()
    # TODO deal with `updated`/`drafted`?
    if "published" in resource:
        # TODO accept simple eg. published=2020-2-20, published=2020-2-20T02:22:22
        # XXX resource["published"][0]["datetime"] = pendulum.from_format(
        # XXX     resource["published"][0]["datetime"], "YYYY-MM-DDTHH:mm:ssZ"
        # XXX )
        # XXX published = resource["published"]
        pass
    else:
        resource["published"] = [
            {
                "datetime": web.utcnow().isoformat(),
                "timezone": config["timezone"],
            }
        ]
    published = pendulum.parse(
        resource["published"][0]["datetime"],
        tz=resource["published"][0]["timezone"],
    )

    resource["visibility"] = resource.get("visibility", ["public"])
    # XXX resource["channel"] = resource.get("channel", [])
    mentions = []
    urls = resource.pop("url", [])
    if resource_type == "card":
        slug = resource.get("nickname", resource.get("name"))[0]
        urls.insert(0, f"/pub/cards/{web.textslug(slug)}")
    elif resource_type == "feed":
        name_slug = web.textslug(resource["name"][0])
        try:
            slug = resource["slug"][0]
        except KeyError:
            slug = name_slug
        resource.update(uid=[slug if slug else name_slug])
        resource.pop("channel", None)
        # XXX urls.insert(0, f"/{slug}")
    elif resource_type == "entry":
        #                                         REQUEST URL
        # 1) given: url=/xyz                        => look for exact match
        #     then: url=[/xyz, /2021/3/5...]
        # 2) given: channel=abc, slug=foo           => construct
        #     then: url=[/2021/3/5...]
        # 3) given: no slug                         => only via permalink
        #     then: url=[/2021/3/5...]
        post_type = discover_post_type(resource)
        slug = None
        if post_type == "article":
            slug = resource["name"][0]
        elif post_type == "bookmark":
            mentions.append(resource["bookmark-of"][0])
        elif post_type == "like":
            mentions.append(resource["like-of"][0])
        elif post_type == "rsvp":
            mentions.append(resource["in-reply-to"][0])
        # elif post_type == "identification":
        #     identifications = resource["identification-of"]
        #     identifications[0] = {"type": "cite",
        #                           **identifications[0]["properties"]}
        #     textslug = identifications[0]["name"]
        #     mentions.append(identifications[0]["url"])
        # elif post_type == "follow":
        #     follows = resource["follow-of"]
        #     follows[0] = {"type": "cite", **follows[0]["properties"]}
        #     textslug = follows[0]["name"]
        #     mentions.append(follows[0]["url"])
        #     tx.sub.follow(follows[0]["url"])
        # TODO user indieauth.server.get_identity() ??
        # XXX author_id = list(db.select("identities"))[0]["card"]
        # XXX author_id = get_card()db.select("resources")[0]["card"]["version"]
        resource.update(author=[tx.origin])
    # elif resource_type == "event":
    #     slug = resource.get("nickname", resource.get("name"))[0]
    #     urls.insert(0, f"/pub/cards/{web.textslug(slug)}")
    #     # if resource["uid"] == str(web.uri(tx.host.name)):
    #     #     pass
    resource.update(url=urls, type=[resource_type])
    permalink_base = f"/{web.timeslug(published)}"

    while True:
        permalink = f"{permalink_base}/{generate_trailer()}"
        resource["url"].append(permalink)
        try:
            db.insert(
                "resources",
                permalink=permalink,
                version=web.nbrandom(10),
                resource=resource,
            )
        except db.IntegrityError:
            continue
        break
    return permalink, mentions


@posts_model.control
def read(db, url):
    """Return an entry with its metadata."""
    if not url.startswith(("http://", "https://")):
        url = f"/{url.strip('/')}"
    try:
        resource = db.select(
            "resources",
            where="""json_extract(resources.resource, '$.url[0]') == ?""",
            vals=[url],
        )[0]
    except IndexError:
        resource = db.select(
            "resources",
            where="""json_extract(resources.resource, '$.alias[0]') == ?""",
            vals=[url],
        )[0]
    r = resource["resource"]
    if "entry" in r["type"]:
        r["author"] = tx.identities.get_identity(r["author"][0])["card"]
    return resource


@posts_model.control
def update(db, url, add=None, replace=None, remove=None):
    """Update a resource."""
    permalink = f"/{url.strip('/')}"
    resource = db.select("resources", where="permalink = ?", vals=[permalink])[0][
        "resource"
    ]
    if add:
        for prop, vals in add.items():
            try:
                resource[prop].extend(vals)
            except KeyError:
                resource[prop] = vals
    if replace:
        for prop, vals in replace.items():
            resource[prop] = vals
    if remove:
        for prop, vals in remove.items():
            del resource[prop]
    resource["updated"] = web.utcnow()
    db.update("resources", resource=resource, where="permalink = ?", vals=[permalink])
    # TODO web.publish(url, f".{prop}[-0:-0]", vals)


@posts_model.control
def delete(db, url):
    """Delete a resource."""
    resource = tx.pub.read(url)
    with db.transaction as cur:
        cur.insert("deleted_resources", **resource)
        cur.delete("resources", where="permalink = ?", vals=[url])


@posts_model.control
def search(db, query):
    """Return a list of resources containing `query`."""
    where = """json_extract(resources.resource,
                   '$.bookmark-of[0].url') == ?
               OR json_extract(resources.resource,
                   '$.like-of[0].url') == ?"""
    return db.select("resources", vals=[query, query], where=where)


@posts_model.control
def get_identity(db, version):
    """Return a snapshot of an identity at given version."""
    return tx.pub.get_version(version)


@posts_model.control
def get_version(db, version):
    """Return a snapshot of resource at given version."""
    return db.select("resources", where="version = ?", vals=[version])[0]


@posts_model.control
def get_entry(db, path):
    """"""


@posts_model.control
def get_card(db, nickname):
    """Return the card with given nickname."""
    resource = db.select(
        "resources",
        vals=[nickname],
        where="""json_extract(resources.resource,
                                         '$.nickname[0]') == ?""",
    )[0]
    return resource["resource"]


@posts_model.control
def get_event(db, path):
    """"""


@posts_model.control
def get_entries(db, limit=20, modified="DESC"):
    """Return a list of entries."""
    return db.select(
        "resources",
        order=f"""json_extract(resources.resource,
                                      '$.published[0]') {modified}""",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'entry'""",
        limit=limit,
    )


@posts_model.control
def get_cards(db, limit=20):
    """Return a list of alphabetical cards."""
    return db.select(
        "resources",  # order="modified DESC",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'card'""",
    )


@posts_model.control
def get_rooms(db, limit=20):
    """Return a list of alphabetical rooms."""
    return db.select(
        "resources",  # order="modified DESC",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'room'""",
    )


@posts_model.control
def get_channels(db):
    """Return a list of alphabetical channels."""
    return db.select(
        "resources",  # order="modified DESC",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'feed'""",
    )


@posts_model.control
def get_categories(db):
    """Return a list of categories."""
    return [
        r["value"]
        for r in db.select(
            "resources, json_each(resources.resource, '$.category')",
            what="DISTINCT value",
        )
    ]


@posts_model.control
def get_posts(db):
    """."""
    for post in db.select(
        "resources",
        where="""json_extract(resources.resource, '$.channel[0]') IS NULL AND
                 json_extract(resources.resource, '$.type[0]') != 'card'""",
        order="""json_extract(resources.resource, '$.published[0]') DESC""",
    ):
        r = post["resource"]
        if "entry" in r["type"]:
            r["author"] = tx.identities.get_identity(r["author"][0])["card"]
        yield r


@posts_model.control
def get_posts_by_channel(db, uid):
    """."""
    return db.select(
        "resources",
        vals=[uid],
        where="""json_extract(resources.resource,
                                     '$.channel[0]') == ?""",
        order="""json_extract(resources.resource,
                                     '$.published[0]') DESC""",
    )


# def get_channels(db):
#     """Return a list of channels."""
#     return [r["value"] for r in
#             db.select("""resources,
#                            json_tree(resources.resource, '$.channel')""",
#                          what="DISTINCT value", where="type = 'text'")]


@posts_model.control
def get_year(db, year):
    return db.select(
        "resources",
        order="""json_extract(resources.resource,
                                     '$.published[0].datetime') ASC""",
        where=f"""json_extract(resources.resource,
                                      '$.published[0].datetime')
                                      LIKE '{year}%'""",
    )


@posts_model.control
def get_media(db):
    """Return a list of media filepaths."""
    try:
        filepaths = list(pathlib.Path(tx.host.name).iterdir())
    except FileNotFoundError:
        filepaths = []
    return filepaths


@posts_model.control
def get_filepath(db, filename):
    """Return a media file's path."""
    return pathlib.Path(tx.host.name) / filename
