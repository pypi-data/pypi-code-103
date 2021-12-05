import mimetypes
from omnitools import encodeURIComponent
# type hints
from omnitools.xtype import *


def transform(
        url,  # type: str
        *,
        is_binary=False,  # type: bool
        assemble=True  # type: bool
) -> Union[str, list]:
    whitelist = [
        "application/json",
        "application/javascript",
        "text/css",
        "image/png",
        "text/html",
        "text/plain",
    ]
    params = url.split("?")
    type = mimetypes.guess_type(params[0])[0]
    is_binary = is_binary or (whitelist and url.count("/") > 2 and type and type not in whitelist)
    api_key = "3cbab51d-6f44-4569-b131-140fd3802204"
    parts = url.split("?")[0].split("/")
    origin = "/".join(parts[:3])
    subdomain = parts[2].replace(".", "-")
    if is_binary:
        path = api_key+"/ajax"
    else:
        path = "/".join(parts[3:])
    extra = "?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=op"
    if url.startswith("http://"):
        extra += "&_x_tr_sch=http"
    if len(params) == 2:
        if is_binary:
            extra += "&u="+encodeURIComponent(origin+"/"+"/".join(parts[3:])+"?"+params[1])
            params = ""
        else:
            params = "&"+params[1]
    else:
        if is_binary:
            extra += "&u="+encodeURIComponent(origin+"/"+"/".join(parts[3:]))
        params = ""
    if assemble:
        return "https://{}.translate.goog/{}{}{}".format(subdomain, path, extra, params)
    else:
        return [
            "https://{}.translate.goog/".format(subdomain),
            path, extra, params
        ]




