def url_join(url, path):
    return "/".join(str(item).strip("/") for item in [url, path] if item is not None)
