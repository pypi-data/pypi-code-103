""""""

import websub
from understory import sql, web
from understory.web import tx

model = sql.model(
    __name__,
    channels={"uid": "TEXT UNIQUE", "name": "TEXT UNIQUE", "unread": "INTEGER"},
    following={
        "person_id": "TEXT UNIQUE",
        "url": "TEXT UNIQUE",
        "added": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    },
)


@model.control
def search(db, query):
    """
    Return a list of feeds associated with given query.

    If query is a URL, fetch it and look for feeds (inline and external).

    """
    # TODO Use canopy.garden for discovery.
    # TODO If query is a keyword, make suggestions.
    url = query
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    resource = tx.cache.add(url)[1]
    feeds = []
    if resource.feed["entries"]:
        feed = {"type": "feed", "url": url, "name": "Unknown"}
        if resource.card:
            feed["name"] = resource.card["name"][0]
            try:
                feed["photo"] = resource.card["photo"]
            except KeyError:
                pass
        feeds.append(feed)
    for url in resource.mf2json["rels"].get("feed", []):
        feed = {"type": "feed", "url": url, "name": "Unknown"}
        subresource = tx.cache.add(url)[1]
        if subresource.card:
            feed["name"] = subresource.card["name"][0]
            try:
                feed["photo"] = subresource.card["photo"]
            except KeyError:
                pass
        feeds.append(feed)
    return feeds


@model.control
def preview(db, url):
    """Return as much information about the URL as possible."""
    resource = tx.cache.add(url)[1]
    items = []
    for entry in resource.feed["entries"]:
        entry["type"] = "entry"
        # item = {"type": "entry"}
        # if "published" in entry:
        #     item["published"] = entry["published"]
        # if "url" in entry:
        #     item["url"] = entry["url"]
        # if "content" in entry:
        #     item["content"] = {
        #         "html": entry["content"],
        #         "text": entry["content-plain"],
        #     }
        # if "category" in entry:
        #     item["category"] = entry["category"]
        # if "photo" in entry:
        #     item["photo"] = entry["photo"]
        # if "syndication" in entry:
        #     item["syndication"] = entry["syndication"]
        items.append(entry)
    return {"items": items}


@model.control
def get_channels(db):
    """Return your subscription channels."""
    return [{"uid": "notifications", "name": "Notifications", "unread": 0}] + [
        {"uid": c["uid"], "name": c["name"], "unread": c["unread"]}
        for c in db.select("channels")
    ]


@model.control
def add_channel(db, name):
    """Add a subscription channels."""
    db.insert("channels", uid=name.lower().replace(" ", "_"), name=name)
    return tx.sub.get_channels()


@model.control
def follow(db, url):
    """Start following the feed at given url."""
    db.insert("following", url=url, person_id=web.nbrandom(3))


@model.control
def get_following(db):
    """Return the feeds you're currently following."""
    return [{"type": "feed", "url": f["url"]} for f in db.select("following")]


# XXX iPhone-compatible CardDAV support below XXX


def generate_vcard(nickname):
    """"""
    card = tx.pub.get_card(nickname)
    vcard = vobject.vCard()
    vcard.add("prodid").value = "-//Canopy//understory 0.0.0//EN"
    vcard.add("uid").value = card["uid"][0]
    vcard.add("fn").value = card["name"][0]
    return vcard.serialize()

    # TODO # TODO if identity["type"] == "identity":
    # TODO n = card.add("n")
    # TODO names = {}
    # TODO for name_type in ("prefix", "given", "additional",
    #                        "family", "suffix"):
    # TODO     if identity[name_type]:
    # TODO         names[name_type] = identity[name_type].split(";")
    # TODO n.value = vobject.vcard.Name(**names)
    # TODO # TODO else:
    # TODO # TODO     card.add("n")
    # TODO # TODO     card.add("org").value = [identity["name"]]

    # TODO # TODO card.add("nickname").value = identity["name"]
    # TODO card.add("sort_string").value = identity["sort_string"]

    # TODO for number, types in identity["telephones"]:
    # TODO     entry = card.add("tel")
    # TODO     entry.value = number
    # TODO     if types:
    # TODO         entry.params["TYPE"] = types

    # TODO for url, types in identity["websites"]:
    # TODO     entry = card.add("url")
    # TODO     entry.value = url
    # TODO     if types:
    # TODO         entry.params["TYPE"] = types

    # TODO try:
    # TODO     photo_id = identity["photos"][0]
    # TODO except IndexError:
    # TODO     pass
    # TODO else:
    # TODO     photo_data = \
    # TODO         canopy.branches["images"].photos.get_photo_data(id=photo_id)
    # TODO     photo = card.add("photo")
    # TODO     photo.value = photo_data
    # TODO     photo.encoding_param = "b"
    # TODO     photo.type_param = "JPEG"

    # item_index = 0
    # for vals in card.contents.values():
    #     for val in vals:
    #         if val.group:
    #             item_index = int(val.group[4:])

    # for related, types in get_relationships(identity["id"]):
    #     uri = "https://{}/identities/{}/{}.vcf".format(tx.host.name,
    #                                                related["identifier"],
    #                                                related["slug"])
    #     rel = card.add("related")
    #     rel.value = uri
    #     rel.params["TYPE"] = types
    #     for type in types:
    #         group_name = "item{}".format(item_index)
    #         rel_name = card.add("x-abrelatednames")
    #         rel_name.value = related["name"]
    #         rel_name.group = group_name
    #         rel_uri = card.add("x-aburi")
    #         rel_uri.value = uri
    #         rel_uri.group = group_name
    #         rel_type = card.add("x-ablabel")
    #         rel_type.value = "_$!<{}>!$_".format(type)
    #         rel_type.group = group_name
    #         item_index += 1
