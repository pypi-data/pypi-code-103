import requests
import json
from datetime import datetime


tstamp_template = "%Y-%m-%dT%H:%M:%S.%f"


class WebhookFailException(Exception):
    """
    Webhook failure handler
    """

    def __init__(self, hook_type: str, error_code: int):
        self.hook_type = hook_type
        self.error_code = error_code


class Webhook:
    """
    Webhook Superclass. Used to make other webhook classes.

    :param hook_url: URL to send webhook data to
    :param summary: Summary of the program, used in the webhook creation
    :param error_limit: Number of messages to send. -1 for no limit, default 10
    :param notify_only: Only notify that messages exist. Useful if there is PII
    :param log_path: Where the physical log is located (if one exists)
    """

    messages = []

    def __init__(
        self,
        hook_url: str,
        summary: str,
        error_limit: int = 10,
        notify_only: bool = False,
        log_path: str = None,
    ):
        self.summary = summary
        self.hook_url = hook_url
        if type(error_limit) == int:
            self.error_limit = error_limit
        else:
            self.error_limit = 10
        if notify_only is True:
            self.notify_only = True
        else:
            self.notify_only = False
        self.log_path = log_path

    def add_message(self, level: str, message: str, tstamp: str):
        """
        Adds a message to the webhook

        :param level: Level of message
        :param message: Log message
        :param tstamp: Timestamp of message
        """
        if self.error_limit > 0 and len(self.messages) < self.error_limit:
            self.messages.append(
                {"level": level, "tstamp": tstamp, "message": message}
            )
        elif len(self.messages) == self.error_limit:
            self.messages[-1] = {
                "level": "WARNING",
                "tstamp": tstamp,
                "message": f"More than {self.error_limit} errors occured. "
                + "Please view logs",
            }

    def send_to_hook(self):
        """
        Sends the data to the webhook
        """
        if len(self.messages) == 0:
            return
        if self.notify_only:
            self.messages = [
                {
                    "level": "INFO",
                    "tstamp": datetime.now().strftime(tstamp_template),
                    "message": "Program had messages, "
                    + "but is in notify-only mode. "
                    + "Please check logs to see messages",
                }
            ]
        msg = self.get_formatted_msg()
        headers = {"Content-Type": "application/json"}
        try:
            req = requests.post(
                self.hook_url, headers=headers, data=json.dumps(msg)
            )
        except ConnectionError as e:
            raise WebhookFailException(
                self.__class__.__name__, e.args[0].message
            )
        if req.status_code < 200 or req.status_code >= 300:
            raise WebhookFailException(
                self.__class__.__name__, req.status_code
            )
        self.messages = []

    def get_formatted_msg(self) -> object:
        """
        Returns the formatted messages for the webhook
        """
        pass


class Teams(Webhook):
    """
    Webhook handler for Microsoft Teams

    :param hook_url: URL to send webhook data to
    :param summary: Summary of the program, used in the webhook creation
    :param error_limit: Number of messages to send. -1 for no limit, default 10
    :param notify_only: Only notify that messages exist. Useful if there is PII
    :param log_path: Where the physical log is located (if one exists)
    :param subtitle: Subtitle to use on Teams message card
    """

    def __init__(
        self,
        hook_url: str,
        summary: str,
        error_limit: int = 10,
        notify_only: bool = False,
        log_path: str = None,
        subtitle: str = None,
    ):
        super().__init__(hook_url, summary, error_limit, notify_only, log_path)
        if subtitle is None:
            if log_path is not None:
                subtitle = log_path
            else:
                subtitle = "No log for this program"
        self.subtitle = subtitle

    def get_formatted_msg(self) -> dict:
        """
        Returns a properly formatted Teams message for sending
        """
        tmp = [x for x in self.messages]
        self.messages = []
        for t in tmp:
            level = t["level"]
            tstamp = t["tstamp"]
            message = t["message"]
            self.messages.append(
                {"name": level, "value": f"[{tstamp}] {message}"}
            )
        teams_message = {
            "@type": "MessageCard",
            "summary": self.summary,
            "sections": [
                {
                    "activityTitle": self.summary,
                    "activitySubtitle": self.subtitle,
                    "facts": self.messages,
                    "markdown": True,
                }
            ],
        }
        return teams_message


class Discord(Webhook):
    """
    Webhook handler for Discord

    :param hook_url: URL to send webhook data to
    :param summary: Summary of the program, used in the webhook creation
    :param error_limit: Number of messages to send. -1 for no limit, default 10
    :param notify_only: Only notify that messages exist. Useful if there is PII
    :param log_path: Where the physical log is located (if one exists)
    :param embed_color: Discord embed color for left bar. Default to UNCO Gold
    """

    def __init__(
        self,
        hook_url: str,
        summary: str,
        error_limit: int = 10,
        notify_only: bool = False,
        log_path: str = None,
        embed_color: int = int("F6B000", 16),  # UNCO Gold
    ):
        super().__init__(hook_url, summary, error_limit, notify_only, log_path)
        self.embed_color = embed_color

    def get_formatted_msg(self) -> dict:
        """
        Returns a properly-formatted Discord embed message
        """
        embed = {
            "color": self.embed_color,
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "Sent using BearLib"},
            "fields": [],
        }
        for message in self.messages:
            embed["fields"].append(
                {
                    "name": message["level"],
                    "value": f"[{message['tstamp']}] {message['message']}",
                }
            )
        discord_message = {"content": self.summary, "embeds": [embed]}
        return discord_message


class Slack(Webhook):
    """
    Webhook handler for Slack

    :param hook_url: URL to send webhook data to
    :param summary: Summary of the program, used in the webhook creation
    :param error_limit: Number of messages to send. -1 for no limit, default 10
    :param notify_only: Only notify that messages exist. Useful if there is PII
    :param log_path: Where the physical log is located (if one exists)
    :param attachment_color: Slack attachment color. Default to UNCO Gold
    """

    def __init__(
        self,
        hook_url: str,
        summary: str,
        error_limit: int = 10,
        notify_only: bool = False,
        log_path: str = None,
        attachment_color: str = "#F6B000",  # UNCO Gold
    ):
        super().__init__(hook_url, summary, error_limit, notify_only, log_path)
        self.attachment_color = attachment_color

    def get_formatted_msg(self) -> dict:
        """
        Returns a properly-formatted Slack message with attachments
        """
        slack_message = {
            "attachments": [
                {
                    "fallback": self.summary,
                    "color": self.attachment_color,
                    "text": self.summary,
                    "fields": [],
                }
            ]
        }
        for message in self.messages:
            slack_message["attachments"][0]["fields"].append(
                {
                    "value": f"[{message['tstamp']}] [{message['level']}]"
                    + " {message['message']}",
                    "short": False,
                }
            )
        return slack_message


types = [Teams, Discord, Slack]


def register_webhook(hook: Webhook) -> str:
    """
    Register a new valid webhook

    :param hook: New webhook class
    """
    if Webhook in hook.__mro__:
        if hook not in types:
            types.append(hook)
            return f"Registered {hook.__class__.__name__} as valid webhook"
        else:
            return f"{hook.__class__.__name__} already registered as valid webhook"
    return f"{hook.__class__.__name__} is not a valid webhook. Please use superclass Webhook"
