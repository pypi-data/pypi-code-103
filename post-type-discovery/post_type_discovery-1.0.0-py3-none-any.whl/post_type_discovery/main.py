# implementation of the post type discovery spec
# see spec on the IndieWeb wiki: https://indieweb.org/post-type-discovery

from bs4 import BeautifulSoup

def get_post_type(h_entry, custom_properties):
    post = h_entry.get("properties")

    if post == None:
        return "unknown"

    values_to_check = [
        ("rsvp", "rsvp"),
        ("in-reply-to", "reply"),
        ("repost-of", "repost"),
        ("like-of", "like"),
        ("video", "video"),
        ("photo", "photo"),
        ("summary", "summary")
    ]

    for property in custom_properties:
        if len(property) == 2 and type(property) == tuple:
            values_to_check.append(property)
        else:
            raise Exception("custom_properties must be a list of tuples")

    for item in values_to_check:
        if post.get(item[0]):
            return item[1]

    post_type = "note"

    if post.get("name") == None or post.get("name")[0] == "":
        return post_type

    title = post.get("name")[0].strip().replace("\n", " ").replace("\r", " ")

    content = post.get("content")

    if content and content[0].get("text") and content[0].get("text")[0] != "":
        content = BeautifulSoup(content[0].get("text"), "lxml").get_text()

    if content and content[0].get("html") and content[0].get("html")[0] != "":
        content = BeautifulSoup(content[0].get("html"), "lxml").get_text()

    if not content.startswith(title):
        return "article"

    return "note"