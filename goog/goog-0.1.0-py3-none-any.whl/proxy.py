import re
import html
import requests


def process(
        url,  # type: str
        *,
        is_binary=None,  # type: bool
        **kwargs
) -> bytes:
    """
    Description: Get content of `url` via Google Translate internal proxy
    Usage: `process("http://example.com")`\\n`process("http://example.com/doc.pdf", is_binary=False)`\\n`process("https://example.com/file.zip?range=0-100", is_binary=True)`

    :param url: the HTTP Uniform Resource Locator
    :param is_binary: is target resource binary?
    :param kwargs: additional `kwargs` for `requests.Session.get`
    :return: resource content in bytes
    """
    def replace(b):
        return re.sub(
            rb'<base href=("|\').*?\1>',
            b"",
            re.sub(
                rb'<script type=("|\')text/javascript\1 src=("|\')https://www.gstatic.com.*?\2></script>',
                b"",
                re.sub(
                    rb'<meta name=("|\')robots\1 content=("|\')none\2>',
                    b"",
                    b
                )
            )
        ).replace(
            html.escape("https://translate.google.com/website?sl=auto&tl=en&anno=2&u="+origin).encode(),
            b""
        ).replace(
            html.escape("https://translate.google.com/website?sl=auto&tl=en&anno=2&u=").encode(),
            b""
        ).replace(
            parts[0].encode(),
            b""
        ).replace(
            html.escape(parts[2]).encode(),
            b""
        ).replace(
            html.escape("&"+parts[2][1:]).encode(),
            b""
        )
    from .cdn import transform
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"})
    parts = transform(url, is_binary=is_binary, assemble=False)
    origin = "/".join(url.split("/")[:3])
    r = s.get("".join(parts), **kwargs)
    if not is_binary and "text/html" in r.headers["Content-Type"]:
        return replace(r.content)
    else:
        return r.content


