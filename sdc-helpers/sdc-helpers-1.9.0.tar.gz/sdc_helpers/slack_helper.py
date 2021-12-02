"""
   SDC Slack helper module
"""
import json
import os
import requests


class SlackHelper:
    """
       Slack helper class to send logs to Slack
    """
    critical_hook = None
    critical_color = '#ff0909'

    def __init__(self):
        self.critical_hook = os.getenv('SLACK_CRITICAL_HOOK')

    @staticmethod
    def send_message(*, hook: str, color: str, message: str):
        """
            Send a message to Slack channel

            args:
                hook (str): The Slack channel's hook URL endpoint
                color (str): Hex color code of the message
                value (str): The content of the message
        """
        data = {
            'attachments': [
                {
                    'title': os.getenv(
                        'AWS_PROCESS_NAME',
                        os.getenv(
                            'AWS_LAMBDA_FUNCTION_NAME',
                            'Unlabelled process'
                        )
                    ),
                    'text': message,
                    'color': color,
                    'mrkdwn_in': ['text']
                }
            ]
        }
        response = requests.post(
            url=hook,
            data=json.dumps(data)
        )

        response_text = response.text
        if response_text != 'ok':
            print('There was an issue posting to Slack: {error}'.format(error=response_text))

    def send_critical(self, *, message: str):
        """
            Send a critical message to the critical Slack channel

            args:
                value (str): The content of the message
        """
        self.send_message(
            hook=self.critical_hook,
            color=self.critical_color,
            message=message
        )
