from typing import Any
from typing import Dict

from dict_tools.data import NamespaceDict


async def gather(hub) -> Dict[str, Any]:
    """
    Get a new access token based on Azure client_id, client_secret and tenant_id

    Example:
    .. code-block:: yaml

        azure:
          profile_name:
            client_id: Azure client id "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            secret: Azure client secret "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            subscription_id: Azure subscription id "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
            tenant: Azure tenant id "cccccccc-cccc-cccc-cccc-cccccccccccc"
    """
    sub_profiles = {}
    for profile, ctx in hub.acct.PROFILES.get("azure", {}).items():
        temp_ctx = NamespaceDict(acct={})
        tenant = ctx["tenant"]
        client_id = ctx["client_id"]
        secret = ctx["secret"]
        subscription_id = ctx["subscription_id"]

        ret = await hub.exec.request.json.post(
            temp_ctx,
            url=f"https://login.microsoftonline.com/{tenant}/oauth2/token",
            headers={
                "content-type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": secret,
                "resource": "https://management.azure.com/",
            },
        )

        if not ret["status"]:
            comment = ret.get("comment", "")
            error = f"Unable to authenticate with tenant '{tenant}' and client id '{client_id}': {comment}"
            hub.log.error(error)
            raise ConnectionError(error)

        access_token = ret["ret"]["access_token"]
        sub_profiles[profile] = dict(
            endpoint_url=f"https://management.azure.com/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return sub_profiles
