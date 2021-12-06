from bs4.element import Tag


def get_text(tag: Tag) -> str:
    return tag.text


def get_attribute(tag: Tag, name: str) -> str:
    return tag.attrs[name]
