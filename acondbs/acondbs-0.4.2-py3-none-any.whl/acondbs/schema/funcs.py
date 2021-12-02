from ..github.ops import get_user_for_token


##__________________________________________________________________||
def get_git_hub_viewer_from_info(info):

    auth = info.context.headers.get("Authorization")
    # e.g., 'Bearer "xxxx"', "Bearer 'xxxx'",  or 'Bearer xxxx'

    if not auth:
        raise Exception("Authorization is required")

    token = auth.split()[1].strip("\"'")
    # e.g., "xxxx"

    return get_user_for_token(token)


##__________________________________________________________________||
