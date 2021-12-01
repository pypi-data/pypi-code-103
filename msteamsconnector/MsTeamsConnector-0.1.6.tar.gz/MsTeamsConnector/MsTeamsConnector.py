import requests
import msal
import json
from pydantic import BaseModel
from datetime import datetime, timedelta
import re


class Credentials(BaseModel):
    CLIENT_ID: str
    AUTHORITY: str
    USERNAME: str
    PASSWORD: str
    SCOPE: list = ['https://graph.microsoft.com/.default']


class Button(BaseModel):
    type: str
    title: str
    value: str
    image: str = ''


class Images(BaseModel):
    url: str
    alt: str


class Member(BaseModel):
    id: str


class Message(BaseModel):
    team_id: str
    channel_id: str
    members_dictionary: dict = {}
    title: str = None
    subtitle: str = None
    text: str = ''
    images: list = []
    buttons: list = []
    entities: list = []
    importance: str = 'normal'
    reply_id: str = None


class MsTeamsConnector():
    def __init__(self, credentials: dict = {}, access_token: str = ''):
        if access_token:
            self.access_token = access_token
            self.token_expires_on = datetime.now() + timedelta(seconds=3550)
        else:
            self.credentials = Credentials(**credentials)
            self.access_token = self.get_access_token()
        self.api_v = 'v1.0'

    def is_valid_token(self) -> bool:
        if self.access_token and self.token_expires_on and datetime.now() < self.token_expires_on:
            return True
        print('INFO: invalid token. Need to refresh')
        return False

    def is_valid_channel(self, team_id: str, channel_id: str) -> bool:
        if channel_id in [x['id'] for x in self.get_joined_channels_in_team(team_id)]:
            return True
        return False

    def get_access_token(self) -> str:
        app = msal.ClientApplication(self.credentials.CLIENT_ID, authority=self.credentials.AUTHORITY)

        # See this page for constraints of Username Password Flow.
        # https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication

        _res = app.acquire_token_by_username_password(self.credentials.USERNAME,
                                                      self.credentials.PASSWORD,
                                                      scopes=self.credentials.SCOPE)
        try:
            self.auth_info = _res
            self.token_expires_on = datetime.now() + timedelta(seconds=3500)
            return _res['access_token']
        except KeyError:
            raise Exception('Error while trying to get access_token::', _res)

    def get_joined_teams(self) -> list:
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        _url = f'https://graph.microsoft.com/{self.api_v}/me/joinedTeams'
        _res = requests.get(url=_url,
                            headers={'Authorization': 'Bearer ' + self.access_token,
                                     'Content-type': 'application/json'},
                            timeout=30)

        if _res.status_code == 200:
            return json.loads(_res.content)['value']
        else:
            raise Exception(f"Error: {_res.content}")

    def get_joined_channels_in_team(self, team_id: str) -> list:
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        _url = f'https://graph.microsoft.com/{self.api_v}/teams/{team_id}/channels'
        _res = requests.get(url=_url,
                            headers={'Authorization': 'Bearer ' + self.access_token,
                                     'Content-type': 'application/json'},
                            timeout=30)

        if _res.status_code == 200:
            return json.loads(_res.content)['value']
        else:
            raise Exception(f"Error: {_res.content}")

    def get_channel_messages(self, team_id: str = '', channel_id: str = '', read_next: bool = False) -> list:
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        if read_next:
            if not self.next_msgs_link:
                raise Exception('No netLink provided. You need to get channel messages first')
            _url = self.next_msgs_link
        else:
            _url = f'https://graph.microsoft.com/beta/teams/{team_id}/channels/{channel_id}/messages'

        _res = requests.get(url=_url,
                            headers={'Authorization': 'Bearer ' + self.access_token,
                                     'Content-type': 'application/json'},
                            timeout=30)

        if _res.status_code == 200:
            _content = json.loads(_res.content)
            try:
                self.next_msgs_link = _content['@odata.nextLink']
            except KeyError:
                pass
            return _content['value']
        else:
            raise Exception(f"Error: {_res.content}")

    def get_message_replies(self, team_id: str = '', channel_id: str = '', message_id: str = '',
                            read_next: bool = False) -> list:
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        if read_next:
            if not self.next_msgs_link:
                raise Exception('No netLink provided. You need to get channel messages first')
            _url = self.next_msgs_link
        else:
            _url = f'https://graph.microsoft.com/beta/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies'

        _res = requests.get(url=_url,
                            headers={'Authorization': 'Bearer ' + self.access_token,
                                     'Content-type': 'application/json'},
                            timeout=30)

        if _res.status_code == 200:
            _content = json.loads(_res.content)
            try:
                self.next_msgs_link = _content['@odata.nextLink']
            except KeyError:
                pass
            return _content['value']
        else:
            raise Exception(f"Error: {_res.content}")

    def get_team_members(self, team_id: str):
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        _url = f'https://graph.microsoft.com/{self.api_v}/groups/{team_id}/members'

        _res = requests.get(url=_url,
                            headers={'Authorization': 'Bearer ' + self.access_token,
                                     'Content-type': 'application/json'},
                            timeout=30)

        if _res.status_code == 200:
            return json.loads(_res.content)['value']
        else:
            raise Exception(f"Error: {_res.content}")

    def create_message(self, team_id, channel_id):
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        if self.is_valid_channel(team_id, channel_id):
            self.message = Message(team_id=team_id, channel_id=channel_id)
            self.message.members_dictionary = self.get_members_dictionary(team_id)
        else:
            raise Exception(
                f'Invalid channel_id {channel_id}. Channel doesn\'t exists or you are not assigned to given Channel')

    def add_title(self, title):
        self.message.title = title

    def add_subtitle(self, subtitle):
        self.message.subtitle = subtitle

    def add_text(self, text):
        self.message.text = text
        self._add_mentions()

    def set_importance(self, prio):
        if prio not in ['high', 'normal']:
            raise ValueError("Incorrect importance value. Must be 'high' or 'normal'")
        self.message.importance = prio

    def set_reply_message(self, reply_id):
        self.message.reply_id = reply_id

    def _add_mentions(self):
        if not self.message.members_dictionary:
            raise Exception('ERROR: Missing members_dictionary. Cant create mentions list')
        r = re.compile('<at>[a-z|A-Z| ]*</at>')
        mentioned_list = [x.replace('<at>', '').replace('</at>', '') for x in r.findall(self.message.text)]
        self.message.entities = []
        for mention in mentioned_list:
            try:
                mention_item = {
                    'id': mentioned_list.index(mention),
                    'mentionText': mention,
                    'mentioned': {
                        'user': {
                            'id': self.message.members_dictionary[mention],
                            'displayName': mention
                        }
                    }
                }
                self.message.text = self.message.text.replace(
                    f'<at>{mention}</at>',
                    f"<at id='{mentioned_list.index(mention)}'>{mention}</at>"
                )
                self.message.entities.append(mention_item)
            except KeyError:
                print(f"WARN: missing mentioned user '{mention}' in channel members")

    def get_members_dictionary(self, team_id):
        _base_members_dictionary = self.get_team_members(team_id)
        members_dictionary = {}
        for member in _base_members_dictionary:
            members_dictionary[member['displayName']] = member['id']
        return members_dictionary

    def send_message(self):
        if not self.is_valid_token():
            self.access_token = self.get_access_token()

        if not self.message:
            raise Exception("No message provided for sending. Please use 'create_message' method to create msg first")

        msg_data = {
            "subject": self.message.title,
            "summary": self.message.subtitle,
            "importance": self.message.importance,
            "body": {
                "contentType": "html",
                "content": f"<div>{self.message.text}\n</div>"
            },
            "mentions": self.message.entities
        }

        if self.message.reply_id:
            _url = f'https://graph.microsoft.com/beta/teams/{self.message.team_id}/channels/{self.message.channel_id}/messages/{self.message.reply_id}/replies'
        else:
            _url = f'https://graph.microsoft.com/beta/teams/{self.message.team_id}/channels/{self.message.channel_id}/messages'

        _res = requests.post(
            url=_url,
            data=json.dumps(msg_data),
            headers={'Authorization': 'Bearer ' + self.access_token, 'Content-type': 'application/json'},
            timeout=30
        )

        print(_res.status_code)
        if _res.status_code == 201:
            return json.loads(_res.content)
        else:
            raise Exception(f"Error: {_res.content}")
