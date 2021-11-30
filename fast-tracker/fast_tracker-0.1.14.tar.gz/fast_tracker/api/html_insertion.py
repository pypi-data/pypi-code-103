# -*- coding: utf-8 -*-
import re

_head_re = re.compile(b'<head[^>]*>', re.IGNORECASE)

_xua_meta_re = re.compile(b"""<\s*meta[^>]+http-equiv\s*=\s*['"]"""
                          b"""x-ua-compatible['"][^>]*>""", re.IGNORECASE)

_charset_meta_re = re.compile(b"""<\s*meta[^>]+charset\s*=[^>]*>""",
                              re.IGNORECASE)

_attachment_meta_re = re.compile(b"""<\s*meta[^>]+http-equiv\s*=\s*['"]"""
                                 b"""content-disposition['"][^>]*content\s*=\s*(?P<quote>['"])"""
                                 b"""\s*attachment(\s*;[^>]*)?(?P=quote)[^>]*>""",
                                 re.IGNORECASE)

_body_re = re.compile(b'<body[^>]*>', re.IGNORECASE)


def insert_html_snippet(data, html_to_be_inserted, search_limit=64 * 1024):
    body = _body_re.search(data[:search_limit])

    if not body:
        return data if len(data) > search_limit else None
    text = html_to_be_inserted()

    if not text:
        return data

    tail, data = data[body.start():], data[:body.start()]

    def insert_at_index(index):
        return b''.join((data[:index], text, data[index:], tail))

    if _attachment_meta_re.search(data):
        return data + tail

    xua_meta = _xua_meta_re.search(data)
    charset_meta = _charset_meta_re.search(data)

    index = max(xua_meta and xua_meta.end() or 0,
                charset_meta and charset_meta.end() or 0)

    if index:
        return insert_at_index(index)

    head = _head_re.search(data)

    if head:
        return insert_at_index(head.end())

    return insert_at_index(body.start())


def verify_body_exists(data):
    return _body_re.search(data)
