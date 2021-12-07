from os import getenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .logger import get_logger


def post_to_slack(message="", channel="#security-alerts", token=None):
    """post message to slack

    :param message: message to send
    :type message: str
    :param channel: Slack channel name(default=#security-alerts)
    :type channel: str
    :param token: bot or user access token. If token is none, SLACK_API_TOKEN environment value will be assigned.
    :type token: str
    :return: `True` if successful, `None` otherwise
    """
    logger = get_logger(__name__)
    token = getenv("SLACK_API_TOKEN", token)
    if not SLACK_API_TOKEN:
        logger.error("SLACK_API_TOKEN not found in the environment")
        return None
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        logger.error(f"Got an error: {e.response['error']}")
        return None
    return True
