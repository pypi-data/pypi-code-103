from typing import Any
from typing import Dict
from typing import List


async def paginate(
    hub, ctx, url: str, success_codes: List = [200], headers: Dict = {}
) -> Dict[str, Any]:
    """
    Paginate items from the given azure url
    :param hub: The redistributed pop central hub.
    :param ctx: A dict with the keys/values for the execution of the Idem run located in
     `hub.idem.RUNS[ctx['run_name']]`.
    :param url: HTTP request url
    :param success_codes: List of HTTP status codes that are considered as "successful" to a request
    :param headers: HTTP request headers
    :return: Response body
    """
    while url:
        ret = await hub.exec.request.json.get(
            ctx,
            url=url,
            success_codes=success_codes,
            headers=headers,
        )
        if not ret["status"]:
            raise ValueError(
                f"Error on requesting GET {url} with status code {ret['status_code']}:"
                f" {ret.get('comment', '')}"
            )
        result = ret["ret"]
        yield result
        url = result.get("nextLink", None)
