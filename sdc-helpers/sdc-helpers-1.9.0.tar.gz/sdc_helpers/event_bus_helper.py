"""
   SDC Event Bus helper module
"""
from datetime import datetime
import uuid
import requests
import json
import boto3
from sdc_helpers.redis_helper import RedisHelper
from sdc_helpers.slack_helper import SlackHelper

class EventBusHelper:
    """
       Event Bus helper class to send logs to Slack
    """
    def send_event(
            self,
            *,
            event_name: str,
            venture_config_id: str = '5e0004d9-760a-4010-a4c4-e44cdd6e78c0',
            payload: dict
    ):
        """
            Send an event to the event bus

            args:
                event_name (str): The events name
                venture_config_id (str): The event bus venture ID for this event
                payload (dict): Payload object
        """
        retry_count = 0
        event = [{
            'events': [event_name],
            'version': '0.3.0',
            'route': 'general',
            'venture_config_id': venture_config_id,
            'venture_reference': str(uuid.uuid4()),
            'created_at': f"{datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z",
            'culture': 'en-GB',
            'payload': payload,
            'action_type': 'other',
            'action_reference': str(uuid.uuid4())
        }]

        redis_helper = RedisHelper()
        slack_helper = SlackHelper()
        cache_key = f"sdc-event-bus-auth-token-{venture_config_id}"
        auth_token = redis_helper.redis_get(key=cache_key)

        if not auth_token:
            try:
                client = boto3.client('secretsmanager')
                response = client.get_secret_value(SecretId='event_bus')
                secret = json.loads(response.get('SecretString'))

                credentials = {
                    'username': secret.get('username'),
                    'password': secret.get('password'),
                    'venture_config_id': venture_config_id
                }
                response = requests.post(
                    url='https://bus.ritdu.net/v1/login',
                    data=json.dumps(credentials)
                )

                auth_token = json.loads(response.text).get('token')

                if not auth_token:
                    slack_helper.send_critical(
                        message=json.dumps(
                            {
                                'error': 'Could not obtain event bus token'
                            }
                        )
                    )
                    return

                redis_helper.redis_set(
                    key=cache_key,
                    value=auth_token
                )
            except Exception as ex:
                slack_helper.send_critical(
                    message=json.dumps(
                        {
                            'error': str(ex)
                        }
                    )
                )

        response = requests.post(
            url='https://bus.ritdu.net/v1/events',
            headers={
                'Accept': 'application/json',
                'Content-type': 'application/json',
                'x-api-key': auth_token
            },
            data=json.dumps(event)
        )

        # Obtain new token if auth failure
        if response.status_code in [401, 403]:
            if retry_count == 5:
                slack_helper.send_critical(
                    message=json.dumps(
                        {
                            'error': f"Authentication issue on Event Bus: {response.text}"
                        }
                    )
                )

            print('Authentication issue - deleting cached auth token and retrying')
            redis_helper.redis_delete(keys=cache_key)
            retry_count += 1
            self.send_event(event_name=event_name, venture_config_id=venture_config_id, payload=payload)
        elif response.status_code != 200:
            slack_helper.send_critical(
                message=json.dumps(
                    {
                        'error': f"Something went wrong on send to Event Bus: {response.text}"
                    }
                )
            )

        return {
            'success': True
        }
