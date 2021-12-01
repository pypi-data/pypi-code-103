from ujson import loads
import asyncio
import aiohttp
from uuid import uuid1
from .util import headers, exceptions, helping, objects

class Client:
    def __init__(self):
        self.mainApi = "http://public.apianon.ru:3000"
        self.chatApi = "https://chat.apianon.ru/api/v1"
        self.mediaRepository = "http://fotoanon.ru"
        self.token = None
        self.clientSession = aiohttp.ClientSession()
        self.headers = headers.Headers().headers
        self.chatHeaders = headers.Headers().chatHeaders

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self.clientSession.close())

    async def _getRocketPassword(self):
        response = await self.clientSession.post(f"{self.mainApi}/users/getRocketPassword", headers = self.headers, json = {})
        body = await response.json()
        return body["data"]["password"]

    async def _chatAuth(self, login: str, rocketPassword: str):
        data = {
            "username": login,
            "password": rocketPassword
        }
        response = await self.clientSession.post(f"{self.chatApi}/login", headers = self.chatHeaders, json = data)
        body = loads(await response.text())
        data = body["data"]
        me = data["me"]
        self.chatUserId = data["userId"]
        self.chatAuthToken = data["authToken"]
        self._chatApiId = me["_id"]
        self.chatHeaders["X-Auth-Token"] = self.chatAuthToken
        self.chatHeaders["X-User-Id"] = self._chatApiId
        return response.status

    async def auth(self, login: str, password: str):
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": helping.randomString(24),
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
        response = await self.clientSession.post(f"{self.mainApi}/users/login2", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.NotLoggedIn(message)
        data = body["data"]
        self.userId = data["id"]
        self.token = data["token"]
        self.name = data["name"]
        self.login = data["login"]
        self.headers["Authorization"] = self.token
        rocketPassword = await self._getRocketPassword()
        await self._chatAuth(login, rocketPassword)
        return response.status
    
    async def register(self, nickname: str, login: str, password: str, setCredentials: bool = True):
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": helping.randomString(16),
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
        response = await self.clientSession.post(f"{self.mainApi}/users/add", headers = self.headers, json = data)
        body = loads(await response.text())
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
            rocketPassword = await self._getRocketPassword()
            await self._chatAuth(login, rocketPassword)
        return response.status
    
    async def getOnlineUsers(self, start: int = 0, size: int = 25):
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
        response = await self.clientSession.post(f"{self.mainApi}/users/recent", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.Unknown(message)
        data = body["data"]
        return objects.UserProfileList(data)
    
    async def startChat(self, targetLogin: str, message: str = None):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "username": targetLogin
        }
        response = await self.clientSession.post(f"{self.chatApi}/im.create", headers = self.chatHeaders, json = data)
        body = loads(await response.text())
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
            response = await self.clientSession.post(f"{self.chatApi}/chat.sendMessage", headers = self.chatHeaders, json = data)
            body = loads(await response.text())
            if not body["success"]:
                message = body["errorType"]
                raise exceptions.MessageSendingError(message)
            return response.status
        return rid

    async def sendMessage(self, message: str, roomId: str):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "message": {
                "_id": str(uuid1()),
                "rid": roomId,
                "msg": message
            }
        }
        response = await self.clientSession.post(f"{self.chatApi}/chat.sendMessage", headers = self.chatHeaders, json = data)
        body = loads(await response.text())
        if not body["success"]:
            message = body["errorType"]
            raise exceptions.MessageSendingError(message)
        return response.status

    async def view(self, postId: int):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": None,
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": postId,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/viewAdd", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.ViewError(message)
        return response.status

    async def like(self, postId: int, autoView: bool = True):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": None,
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": postId,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/likeAdd", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.LikeError(message)
        if autoView:
            await self.view(postId)
        return response.status
    
    async def unlike(self, postId: int, autoView: bool = True):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": None,
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": postId,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/likeDelete", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.LikeError(message)
        if autoView:
            await self.view(postId)
        return response.status
    
    async def repost(self, postId: int, autoView: bool = True):
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": None,
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": postId,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 0,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/repost", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.CommentingError(message)
        if autoView:
            await self.view(postId)
        return response.status

    async def comment(self, postId: int, comment: str, autoView: bool = True):
        if not self.token:
            raise exceptions.Unauthorized()
        if len(comment) < 3:
            raise exceptions.InvalidCommentLenght()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": 0,
            "device": None,
            "device_id": None,
            "filter": None,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": postId,
            "post_ids": None,
            "search": None,
            "text": comment,
            "type": 0,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/commentAdd", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.CommentingError(message)
        if autoView:
            await self.view(postId)
        return response.status
    

    async def getRecentPosts(self, count: int = 50, userFilters: list = None):
        if not self.token:
            raise exceptions.Unauthorized()
        if not userFilters:
            filters = [
                        122,
                        93,
                        76,
                        78,
                        75,
                        74,
                        95,
                        113,
                        96,
                        81,
                        103,
                        65,
                        66,
                        89,
                        82,
                        72,
                        79,
                        86,
                        80,
                        71,
                        68,
                        83,
                        98,
                        84,
                        85,
                        124,
                        91,
                        88,
                        99,
                        101,
                        109,
                        110,
                        111,
                        117,
                        118,
                        108,
                        125,
                        126,
                        112,
                        115,
                        120,
                        121,
                        128,
                        129,
                        131,
                        132,
                        133,
                        134,
                        135,
                        136,
                        69,
                        70,
                        73,
                        77,
                        67,
                        107,
                        106,
                        114,
                        137,
                        138,
                        139,
                        140,
                        141,
                        142,
                        143,
                        130,
                        127,
                        123,
                        119,
                        116,
                        97
                    ]
        else:
            filters = userFilters
        if not self.token:
            raise exceptions.Unauthorized()
        data = {
            "anonim": 0,
            "comment_id": 0,
            "count": count,
            "device": None,
            "device_id": None,
            "filter": filters,
            "gcm": None,
            "hidden": 0,
            "id": 0,
            "last_message": 0,
            "login": None,
            "name": None,
            "object_id": 0,
            "offset": 0,
            "owner_id": 0,
            "password": None,
            "post_id": 0,
            "post_ids": None,
            "search": None,
            "text": None,
            "type": 1,
            "user_id": None
        }
        response = await self.clientSession.post(f"{self.mainApi}/posts/get", headers = self.headers, json = data)
        body = loads(await response.text())
        if body["error"]:
            message = body["message"]
            raise exceptions.Unknown(message)
        data = body["data"]
        return objects.PostList(data)