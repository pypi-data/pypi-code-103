from ujson import loads
import requests
from uuid import uuid1
from .util import headers, exceptions, helping, objects

class Client:
    def __init__(self):
        self.mainApi = "http://public.apianon.ru:3000"
        self.chatApi = "https://chat.apianon.ru/api/v1"
        self.mediaRepository = "http://fotoanon.ru"
        self.token = None
        self.headers = headers.Headers().headers
        self.chatHeaders = headers.Headers().chatHeaders

    def _getRocketPassword(self):
        return requests.post(f"{self.mainApi}/users/getRocketPassword", headers = self.headers, json = {}).json()["data"]["password"]

    def _chatAuth(self, login: str, rocketPassword: str):
        data = {
            "username": login,
            "password": rocketPassword
        }
        response = requests.post(f"{self.chatApi}/login", headers = self.chatHeaders, json = data)
        body = loads(response.text)
        data = body["data"]
        me = data["me"]
        self.chatUserId = data["userId"]
        self.chatAuthToken = data["authToken"]
        self._chatApiId = me["_id"]
        self.chatHeaders["X-Auth-Token"] = self.chatAuthToken
        self.chatHeaders["X-User-Id"] = self._chatApiId
        return response.status_code

    def auth(self, login: str, password: str):
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": "138268d66411a99fasd5fghj",
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": login,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": password,
            "post_id": 0,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = requests.post(f"{self.mainApi}/users/login2", headers = self.headers, json = data)
        body = loads(response.text)
        if body["error"]:
            message = body["message"]
            raise exceptions.NotLoggedIn(message)
        data = body["data"]
        self.userId = data["id"]
        self.token = data["token"]
        self.name = data["name"]
        self.login = data["login"]
        self.headers["Authorization"] = self.token
        rocketPassword = self._getRocketPassword()
        self._chatAuth(login, rocketPassword)
        return response.status_code
    
    def register(self, nickname: str, login: str, password: str, setCredentials: bool = True):
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": "138268d66411a99f",
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login":login,
            "name": nickname,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": password,
            "post_id": 0,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = requests.post(f"{self.mainApi}/users/add", headers = self.headers, json = data)
        body = loads(response.text)
        if body["error"]:
            message = body["message"]
            raise exceptions.NotRegistered(message)
        if setCredentials:
            data = body["data"]
            self.userId = data["id"]
            self.token = data["token"]
            self.name = data["name"]
            self.login = data["login"]
            self.headers["Authorization"] = self.token
            rocketPassword = self._getRocketPassword()
            self._chatAuth(login, rocketPassword)
        return response.status_code
    
    def getOnlineUsers(self, start: int = 0, size: int = 25):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "age_end": 0,
            "age_start": 0,
            "ages": None,
            "city": None,
            "country": 0,
            "find": None,
            "from": start,
            "interests": None,
            "name": None,
            "portion": 2,
            "sex": 0,
            "size": size,
            "target": 0
        }
        response = requests.post(f"{self.mainApi}/users/recent", headers = self.headers, json = data)
        body = loads(response.text)
        if body["error"]:
            message = body["message"]
            raise exceptions.Unknown(message)
        data = body["data"]
        return objects.UserProfileList(data)
    
    def startChat(self, targetLogin: str, message: str = None):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "username": targetLogin
        }
        response = requests.post(f"{self.chatApi}/im.create", headers = self.chatHeaders, json = data)
        body = loads(response.text)
        if not body["success"]:
            message = body["errorType"]
            raise exceptions.ChatNotCreated(message)
        rid = body["room"]["_id"]
        if message:
            data = {
                "message": {
                    "_id": str(uuid1()),
                    "rid": rid,
                    "msg": message
                }
            }
            response = requests.post(f"{self.chatApi}/chat.sendMessage", headers = self.chatHeaders, json = data)
            body = loads(response.text)
            if not body["success"]:
                message = body["errorType"]
                raise exceptions.MessageSendingError(message)
            return response.status_code
        return rid

    def sendMessage(self, message: str, roomId: str):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "message": {
                "_id": str(uuid1()),
                "rid": roomId,
                "msg": message
            }
        }
        response = requests.post(f"{self.chatApi}/chat.sendMessage", headers = self.chatHeaders, json = data)
        body = loads(response.text)
        if not body["success"]:
            message = body["errorType"]
            raise exceptions.MessageSendingError(message)
        return response.status_code