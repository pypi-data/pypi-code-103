import mimetypes


def transform(
        url,  # type: str
        whitelist=(
            "application/json",
            "application/javascript",
            "text/css",
            "image/png",
            "text/html",
            "text/plain",
        )  # type: tuple
) -> str:
    type = mimetypes.guess_type(url)[0]
    if whitelist and url.count("/") > 2 and type not in whitelist:
        raise ValueError("type '{}' cannot be transformed.\nreason: google does not process that resource.".format(type))
    parts = url.split("/")
    subdomain = parts[2].replace(".", "-")
    path = "/".join(parts[3:])
    return "https://{}.translate.goog/{}".format(subdomain, path)




