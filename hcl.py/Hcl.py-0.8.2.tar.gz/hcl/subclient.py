import json
import base64
import time
from uuid import UUID
from os import urandom
from time import timezone
from typing import BinaryIO
from binascii import hexlify
from time import time as timestamp
from json_minify import json_minify

from . import client, settings
from .src import exceptions_v2, exceptions, headers, objects, debugs


class VCHeaders:
    def __init__(self, data=None):
        vc_headers = {
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "User-Agent": "Amino/45725 CFNetwork/1126 Darwin/19.5.0",  # Closest server (this one for me)
            "Host": "rt.applovin.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "Keep-Alive",
            "Accept": "*/*"
        }

        if data: vc_headers["Content-Length"] = str(len(data))
        self.vc_headers = vc_headers


# =========== SUBCLIENT CLASS ===========
class SubClient(client.Client):
    def __init__(self, comId: str = None, aminoId: str = None):
        client.Client.__init__(self)
        self.vc_connect = False

        if not headers.sid:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().notLoggedIn()
            else:
                raise exceptions.NotLoggedIn()

        if comId is not None:
            self.comId = comId
            self.community: objects.Community = self.get_community_info(comId)

        if aminoId is not None:
            self.comId = client.Client().search_community(aminoId).comId[0]
            self.community: objects.Community = client.Client().get_community_info(self.comId)

        if comId is None and aminoId is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList().noCommunity()
            else:
                raise exceptions.NoCommunity()

        try:
            self.profile: objects.UserProfile = self.get_user_info(userId=headers.userId)
        except AttributeError:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().failedLogin()
            else:
                raise exceptions.FailedLogin()
        except exceptions.UserUnavailable:
            pass

    # =========== GET INVITE CODES ===========

    def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.InviteCodeList(json.loads(response.text)["communityInvitationList"]).InviteCodeList

    # ========= GENERATE INVITE CODES ========

    def generate_invite_code(self, duration: int = 0, force: bool = True):
        data = json.dumps({
            "duration": duration,
            "force": force,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/g/s-x{self.comId}/community/invitation",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.InviteCode(json.loads(response.text)["communityInvitation"]).InviteCode

    # ========== DELETE INVITE CODE ==========

    def delete_invite_code(self, inviteId: str):
        response = self.session.delete(f"{self.api}/g/s-x{self.comId}/community/invitation/{inviteId}",
                                       headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== POST BLOG ==============

    def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None,
                  categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False,
                  extensions: dict = None, crash: bool = False):
        mediaList = []

        if captionList is not None:
            for image, caption in zip(imageList, captionList):
                mediaList.append([100, self.upload_media(image, "image"), caption])

        else:
            if imageList is not None:
                for image in imageList:
                    print(self.upload_media(image, "image"))
                    mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "address": None,
            "content": content,
            "title": title,
            "mediaList": mediaList,
            "extensions": extensions,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== POST BLOG (RAW) ===========

    def post_blog_raw(self, raw):
        data = json.dumps(raw)
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== POST WIKI ===============

    def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None,
                  backgroundColor: str = None, fansOnly: bool = False):
        mediaList = []

        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "label": title,
            "content": content,
            "mediaList": mediaList,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}

        response = self.session.post(f"{self.api}/x{self.comId}/s/item", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =============== EDIT BLOG ==============

    def edit_blog(self, blogId: str, title: str = None, content: str = None, imageList: list = None,
                  categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False):
        mediaList = []

        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "address": None,
            "mediaList": mediaList,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        }

        if title: data["title"] = title
        if content: data["content"] = content
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ EDIT BLOG RAW ============

    def edit_blog_raw(self, blogId: str, raw):
        data = json.dumps(raw)
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= DELETE BLOG =============

    def delete_blog(self, blogId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== DELETE WIKI =============

    def delete_wiki(self, wikiId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= REPOST BLOG =============

    def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None):
        if blogId is not None:
            refObjectId, refObjectType = blogId, 1
        elif wikiId is not None:
            refObjectId, refObjectType = wikiId, 2
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        data = json.dumps({
            "content": content,
            "refObjectId": refObjectId,
            "refObjectType": refObjectType,
            "type": 2,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =============== CHECK-IN ==============

    def check_in(self, tz: int = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ REPAIR CHECK-IN ===========

    def repair_check_in(self, method: int = 0):
        data = {"timestamp": int(timestamp() * 1000)}
        if method == 0: data["repairMethod"] = "1"  # Coins
        if method == 1: data["repairMethod"] = "2"  # Amino+

        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in/repair", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =============== LOTTERY ===============

    def lottery(self, tz: int = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in/lottery", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.LotteryLog(json.loads(response.text)["lotteryLog"]).LotteryLog

    # ============= EDIT PROFILE =============

    def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None,
                     chatRequestPrivilege: str = None, imageList: list = None, captionList: list = None,
                     backgroundImage: str = None, backgroundColor: str = None, titles: list = None, colors: list = None,
                     defaultBubbleId: str = None):
        mediaList = []

        data = {"timestamp": int(timestamp() * 1000)}

        if captionList is not None:
            for image, caption in zip(imageList, captionList):
                mediaList.append([100, self.upload_media(image, "image"), caption])

        else:
            if imageList is not None:
                for image in imageList:
                    mediaList.append([100, self.upload_media(image, "image"), None])

        if imageList is not None or captionList is not None:
            data["mediaList"] = mediaList

        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = self.upload_media(icon, "image")
        if content: data["content"] = content

        if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
        if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        if titles or colors:
            tlt = []
            for titles, colors in zip(titles, colors):
                tlt.append({"title": titles, "color": colors})

            data["extensions"] = {"customTitles": tlt}

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== VOTE POLL ==============

    def vote_poll(self, blogId: str, optionId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== COMMENT ==============

    def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False, asWeb: bool = False):
        if asWeb is True:
            data = {"ndcId": self.comId, "content": message}
            if blogId:
                data["postType"] = "blog"; postId = blogId
            elif wikiId:
                data["postType"] = "wiki"; postId = wikiId
            elif userId:
                data["postType"] = "user"; postId = userId
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()
            data["postId"] = postId

            response = self.session.post("https://aminoapps.com/api/submit_comment", json=data,
                                         headers=self.web_headers())
            try:
                if "data-comment-id" in response.json()["result"]["html"]:
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            data = {
                "content": message,
                "stickerId": None,
                "type": 0,
                "timestamp": int(timestamp() * 1000)
            }

            if replyTo: data["respondTo"] = replyTo

            if isGuest:
                comType = "g-comment"
            else:
                comType = "comment"

            if userId:
                data["eventSource"] = "UserProfileView"

                response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{comType}",
                                             headers=self.headers(data=data), json=data)

            elif blogId:
                data["eventSource"] = "PostDetailView"

                response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/{comType}",
                                             headers=self.headers(data=data), json=data)

            elif wikiId:
                data["eventSource"] = "PostDetailView"

                response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/{comType}",
                                             headers=self.headers(data=data), json=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # =========== DELETE COMMENT ===========

    def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}",
                                           headers=self.headers())
        elif blogId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}",
                                           headers=self.headers())
        elif wikiId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}",
                                           headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== LIKE BLOG ===============

    def like_blog(self, blogId: [str, list] = None, wikiId: str = None, asWeb: bool = False):
        postId = ""
        if asWeb is True:
            data = {"ndcId": self.comId}
            if blogId:
                if isinstance(blogId, str):
                    pass
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        return exceptions_v2.ExceptionList().wrongType()
                    else:
                        raise exceptions.WrongType()

            if blogId: data["logType"] = "blog"; data["postType"] = "blog"; postId = blogId
            if wikiId: data["logType"] = "wiki"; data["postType"] = "wiki"; postId = wikiId
            data["postId"] = postId
            response = self.session.post("https://aminoapps.com/api/vote", json=data, headers=self.web_headers())
            try:
                if response.json()["result"]['api:message'] == "OK":
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            data = {
                "value": 4,
                "timestamp": int(timestamp() * 1000)
            }

            if blogId:
                if isinstance(blogId, str):
                    data["eventSource"] = "UserProfileView"

                    response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?cv=1.2",
                                                 headers=self.headers(data=data), json=data)

                elif isinstance(blogId, list):
                    data["targetIdList"] = blogId

                    response = self.session.post(f"{self.api}/x{self.comId}/s/feed/vote",
                                                 headers=self.headers(data=data), json=data)

                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        return exceptions_v2.ExceptionList().wrongType()
                    else:
                        raise exceptions.WrongType()

            elif wikiId:
                data["eventSource"] = "PostDetailView"

                response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/vote?cv=1.2",
                                             headers=self.headers(data=data), json=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # ============= UNLIKE BLOG =============

    def unlike_blog(self, blogId: str = None, wikiId: str = None, asWeb: bool = False):
        if asWeb is True:
            data = {"ndcId": self.comId, }
            if blogId:
                data["logType"] = "blog"; data["postType"] = "blog"; postId = blogId
            elif wikiId:
                data["logType"] = "wiki"; data["postType"] = "wiki"; postId = wikiId
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()
            data["postId"] = postId
            response = self.session.post("https://aminoapps.com/api/unvote", json=data, headers=self.web_headers())
            try:
                if response.json()["result"]['api:message'] == "OK":
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            if blogId:
                response = self.session.delete(
                    f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView",
                    headers=self.headers())
            elif wikiId:
                response = self.session.delete(
                    f"{self.api}/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView", headers=self.headers())
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().specifyType()
                else:
                    raise exceptions.SpecifyType()

            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # ============ LIKE COMMENT ============

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "value": 1,
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["eventSource"] = "UserProfileView"

            response = self.session.post(
                f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1",
                headers=self.headers(data=data), json=data)

        elif blogId:
            data["eventSource"] = "PostDetailView"

            response = self.session.post(
                f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1",
                headers=self.headers(data=data), json=data)

        elif wikiId:
            data["eventSource"] = "PostDetailView"

            response = self.session.post(
                f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1",
                headers=self.headers(data=data), json=data)

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== UNLIKE COMMENT ============

    def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId:
            response = self.session.delete(
                f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView",
                headers=self.headers())
        elif blogId:
            response = self.session.delete(
                f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView",
                headers=self.headers())
        elif wikiId:
            response = self.session.delete(
                f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== UPVOTE COMMENT ==========

    def upvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(
            f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1",
            headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= DOWNVOTE COMMENT ==========

    def downvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": -1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(
            f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=-1",
            headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== UNVOTE COMMENT ============

    def unvote_comment(self, blogId: str, commentId: str):
        response = self.session.delete(
            f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== REPLY WALL =============

    def reply_wall(self, userId: str, commentId: str, message: str):
        data = json.dumps({
            "content": message,
            "stackedId": None,
            "respondTo": commentId,
            "type": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== SEND ACTIVE OBJECT ==========

    def send_active_obj(self, asWeb: bool = False, optInAdsFlags: int = 2147483647, tz: int = -timezone // 1000, timers: list = None, timestmp: int = int(timestamp() * 1000)):
        if asWeb is True:
            data = {"ndcId": self.comId}

            response = self.session.post("https://aminoapps.com/api/community/stats/web-user-active-time", json=data, headers=self.web_headers())
            try:
                if response.json()["code"] != 200: return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
                    else: exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
                else: exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            data = {
                "userActiveTimeChunkList": [{
                    "start": int(time.time()),
                    "end": int(time.time()) + 300
                }],
                "timestamp": timestmp,
                "optInAdsFlags": optInAdsFlags,
                "timezone": tz
            }

            if timers:
                data["userActiveTimeChunkList"] = timers

            data = json_minify(json.dumps(data))
            response = self.session.post(f"{self.api}/x{self.comId}/s/community/stats/user-active-time",
                                         headers=self.headers(data=data), json=data)
            if response.status_code != 200:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # =========== ACTIVITY STATUS ============

    def activity_status(self, status: str):
        if "on" in status.lower():
            status = 1
        elif "off" in status.lower():
            status = 2
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        data = json.dumps({
            "onlineStatus": status,
            "duration": 86400,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/online-status",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= CHECK NOTIFICATIONS ==========

    def check_notifications(self):
        response = self.session.post(f"{self.api}/x{self.comId}/s/notification/checked", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= DELETE NOTIFICATIONS =========

    def delete_notification(self, notificationId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/notification/{notificationId}",
                                       headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= CLEAR NOTIFICATIONS ==========

    def clear_notifications(self):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/notification", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= START CHAT ==============

    def start_chat(self, userId: [str, list], message: str, title: str = None, content: str = None,
                   isGlobal: bool = False, publishToGlobal: bool = False, asWeb: bool = False):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        if asWeb is True:
            data = {
                "ndcId": self.comId,
                "inviteeUids": userIds,
                "initialMessageContent": message,
            }

            if isGlobal is True:
                data["type"] = 2
            else:
                data["type"] = 0

            response = self.session.post("https://aminoapps.com/api/create-chat-thread", json=data,
                                         headers=self.web_headers())
            try:
                if response.json()["result"]['api:message'] == "OK":
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            data = {
                "title": title,
                "inviteeUids": userIds,
                "initialMessageContent": message,
                "content": content,
                "timestamp": int(timestamp() * 1000)
            }

            if isGlobal is True:
                data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
            else:
                data["type"] = 0

            if publishToGlobal is True:
                data["publishToGlobal"] = 1
            else:
                data["publishToGlobal"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread", json=data,
                                         headers=self.headers(data=data))
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # ============ INVITE TO CHAT ============

    def invite_to_chat(self, userId: [str, list], chatId: str):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        data = json.dumps({
            "uids": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/invite",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== ADD TO FAVORITES ===========

    def add_to_favorites(self, userId: str):
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-group/quick-access/{userId}",
                                     headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= SEND COINS ==============

    def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None,
                   transactionId: str = None):
        url = None
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(timestamp() * 1000)
        }

        if blogId is not None: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping"
        if chatId is not None: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping"
        if objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.api}/x{self.comId}/s/tipping"

        if url is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        response = self.session.post(url, headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== THANK TIP ==============

    def thank_tip(self, chatId: str, userId: str):
        response = self.session.post(
            f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =============== FOLLOW ===============

    def follow(self, userId: [str, list], asWeb: bool = False):

        #        Follow an User or Multiple Users.

        #        **Parameters**
        #            - **userId** : ID of the User or List of IDs of the Users.

        #        **Returns**
        #            - **Success** : 200 (int)

        #            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`

        if asWeb is True:
            data = {
                "ndcId": f"x{self.comId}",
                "followee_id": userId
            }
            response = self.session.post("https://aminoapps.com/api/follow-user", json=data, headers=self.web_headers())
            try:
                if response.json()["code"] != 200:
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            if isinstance(userId, str):
                response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member",
                                             headers=self.headers())

            elif isinstance(userId, list):
                data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
                response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined",
                                             headers=self.headers(data=data), json=data)

            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().wrongType()
                else:
                    raise exceptions.WrongType()

            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # ============= UNFOLLOW ===============

    def unfollow(self, userId: str, asWeb: bool = False):
        if asWeb is True:
            data = {
                "ndcId": f"x{self.comId}",
                "followee_id": userId,
                "follower_id": self.userId()
            }
            response = self.session.post("https://aminoapps.com/api/unfollow-user", json=data,
                                         headers=self.web_headers())
            try:
                if response.json()["code"] != 200:
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            response = self.session.delete(
                f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}",
                headers=self.headers())
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # =============== BLOCK =================

    def block(self, userId: str):
        response = self.session.post(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== UNBLOCK ===============

    def unblock(self, userId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ================ VISIT =================

    def visit(self, userId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}?action=visit",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ================ FLAG =================

    def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None,
             asGuest: bool = False):

        #        Flag a User, Blog or Wiki.

        #        **Parameters**
        #            - **reason** : Reason of the Flag.
        #            - **flagType** : Type of the Flag.
        #            - **userId** : ID of the User.
        #            - **blogId** : ID of the Blog.
        #            - **wikiId** : ID of the Wiki.
        #            - *asGuest* : Execute as a Guest.

        if reason is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().reasonNeeded()
            else:
                raise exceptions.ReasonNeeded()
        if flagType is None:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().flagTypeNeeded()
            else:
                raise exceptions.FlagTypeNeeded()

        data = {
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["objectId"] = userId
            data["objectType"] = 0

        elif blogId:
            data["objectId"] = blogId
            data["objectType"] = 1

        elif wikiId:
            data["objectId"] = wikiId
            data["objectType"] = 2

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        if asGuest:
            flg = "g-flag"
        else:
            flg = "flag"

        response = self.session.post(f"{self.api}/x{self.comId}/s/{flg}", json=data, headers=self.headers(data=data))
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ SEND MESSAGE ============

    def send_message(self, chatId: str, asWeb: bool = False, message: str = None, messageType: int = 0,
                     icon: str = None, file: BinaryIO = None, fileType: str = None, replyTo: str = None,
                     mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None,
                     embedLink: str = None, embedTitle: str = None, embedContent: str = None,
                     embedImage: BinaryIO = None, linkSnippet: str = None, linkSnippetImage: BinaryIO = None):

        #        Send a Message to a Chat.

        #        **Parameters**
        #            - **message** : Message to be sent
        #            - **chatId** : ID of the Chat.
        #            - **file** : File to be sent.
        #            - **fileType** : Type of the file.
        #                - ``audio``, ``image``, ``gif``
        #            - **messageType** : Type of the Message.
        #            - **mentionUserIds** : List of User IDS to mention. '@' needed in the Message.
        #            - **replyTo** : Message ID to reply to.
        #            - **stickerId** : Sticker ID to be sent.
        #            - **embedTitle** : Title of the Embed.
        #            - **embedContent** : Content of the Embed.
        #            - **embedLink** : Link of the Embed.
        #            - **embedImage** : Image of the Embed.
        #            - **embedId** : ID of the Embed.
        #            - **linkSnippet** : Link of the target snippet.
        #            - **linkSnippetImage** : Image target snippet.

        if asWeb is True:
            data = {
                "ndcId": f"x{self.comId}",
                "threadId": chatId,
                "message": {"content": message, "mediaType": 0, "type": messageType, "sendFailed": False,
                            "clientRefId": 0}
            }

            if icon:
                data["message"]["content"] = None
                data["message"]["uploadId"] = 0
                data["message"]["mediaType"] = 100
                data["message"]["mediaValue"] = icon

            response = self.session.post("https://aminoapps.com/api/add-chat-message", json=data,
                                         headers=self.web_headers())
            try:
                if response.json()["code"] != 200:
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            if message is not None and file is None:
                message = message.replace("<$", "‎‏").replace("$>", "‬‭")

            mentions = []
            if mentionUserIds:
                for mention_uid in mentionUserIds:
                    mentions.append({"uid": mention_uid})

            if embedImage:
                embedImage = [[100, self.upload_media(embedImage, "image"), None]]

            if linkSnippetImage:
                linkSnippetImage = base64.b64encode(linkSnippetImage.read()).decode()

            data = {
                "type": messageType,
                "content": message,
                "clientRefId": int(timestamp() / 10 % 1000000000),
                "attachedObject": {
                    "objectId": embedId,
                    "objectType": embedType,
                    "link": embedLink,
                    "title": embedTitle,
                    "content": embedContent,
                    "mediaList": embedImage
                },
                "extensions": {
                    "mentionedArray": mentions,
                    "linkSnippetList": [{
                        "link": linkSnippet,
                        "mediaType": 100,
                        "mediaUploadValue": linkSnippetImage,
                        "mediaUploadValueContentType": "image/png"
                    }]
                },
                "timestamp": int(timestamp() * 1000)
            }

            if replyTo: data["replyMessageId"] = replyTo

            if stickerId:
                data["content"] = None
                data["stickerId"] = stickerId
                data["type"] = 3

            if file:
                data["content"] = None
                if fileType == "audio":
                    data["type"] = 2
                    data["mediaType"] = 110

                elif fileType == "image":
                    data["mediaType"] = 100
                    data["mediaUploadValueContentType"] = "image/jpg"
                    data["mediaUhqEnabled"] = True

                elif fileType == "gif":
                    data["mediaType"] = 100
                    data["mediaUploadValueContentType"] = "image/gif"
                    data["mediaUhqEnabled"] = True

                data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

            #  else:
            #      if self.exceptV2 is True or settings.exceptV2 is True:
            #          return exceptions_v2.ExceptionList().specifyType()
            #      else:
            #          raise exceptions.SpecifyType()

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message",
                                         headers=self.headers(data=data), json=data)
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # =========== DELETE MESSAGE ============

    def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):

        #        Delete a Message from a Chat.

        #        **Parameters**
        #            - **messageId** : ID of the Message.
        #            - **chatId** : ID of the Chat.
        #            - **asStaff** : If execute as a Staff member (Leader or Curator).
        #            - **reason** : Reason of the action to show on the Moderation History.

        data = {
            "adminOpName": 102,
            # "adminOpNote": {"content": reason},
            "timestamp": int(timestamp() * 1000)
        }
        if asStaff and reason:
            data["adminOpNote"] = {"content": reason}

        if not asStaff:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}",
                                           headers=self.headers())
        else:
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin",
                                         headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ MARK AS READ =============

    def mark_as_read(self, chatId: str, messageId: str):
        data = json.dumps({
            "messageId": messageId,
            "timestamp": int(timestamp() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/mark-as-read",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============== EDIT CHAT ==============

    def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None,
                  icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None,
                  coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None,
                  publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None,
                  fansOnly: bool = None):

        #        Send a Message to a Chat.

        #        **Parameters**
        #            - **chatId** : ID of the Chat.
        #            - **title** : Title of the Chat.
        #            - **content** : Content of the Chat.
        #            - **icon** : Icon of the Chat.
        #            - **backgroundImage** : Url of the Background Image of the Chat.
        #            - **announcement** : Announcement of the Chat.
        #            - **pinAnnouncement** : If the Chat Announcement should Pinned or not.
        #            - **coHosts** : List of User IDS to be Co-Host.
        #            - **keywords** : List of Keywords of the Chat.
        #            - **viewOnly** : If the Chat should be on View Only or not.
        #            - **canTip** : If the Chat should be Tippable or not.
        #            - **canInvite** : If the Chat should be Invitable or not.
        #            - **fansOnly** : If the Chat should be Fans Only or not.
        #            - **publishToGlobal** : If the Chat should show on Public Chats or not.
        #            - **doNotDisturb** : If the Chat should Do Not Disturb or not.
        #            - **pinChat** : If the Chat should Pinned or not.

        data = {"timestamp": int(timestamp() * 1000)}

        if title: data["title"] = title
        if content: data["content"] = content
        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if announcement: data["extensions"] = {"announcement": announcement}
        if pinAnnouncement: data["extensions"] = {"pinAnnouncement": pinAnnouncement}
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}

        if publishToGlobal: data["publishToGlobal"] = 0
        if not publishToGlobal: data["publishToGlobal"] = 1

        res = []

        if doNotDisturb is not None:
            if doNotDisturb:
                data = json.dumps({"alertOption": 2, "timestamp": int(timestamp() * 1000)})
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(timestamp() * 1000)})
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

        if pinChat is not None:
            if pinChat:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/pin", json=data,
                                             headers=self.headers())
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if not pinChat:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/unpin", json=data,
                                             headers=self.headers())
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

        if backgroundImage is not None:
            data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(timestamp() * 1000)})
            response = self.session.post(
                f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/background", json=data,
                headers=self.headers(data=data))
            if json.loads(response.text)['api:statuscode'] != 0:
                res.append(exceptions.CheckException(json.loads(response.text)))
            else:
                res.append(json.loads(response.text)['api:statuscode'])
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")

        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(timestamp() * 1000)})
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/co-host", json=data,
                                         headers=self.headers(data=data))
            if json.loads(response.text)['api:statuscode'] != 0:
                res.append(exceptions.CheckException(json.loads(response.text)))
            else:
                res.append(json.loads(response.text)['api:statuscode'])
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")

        if viewOnly is not None:
            if viewOnly:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/enable",
                                             json=data, headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if not viewOnly:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/disable",
                                             json=data, headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

        if canInvite is not None:
            if canInvite:
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/enable", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if not canInvite:
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/disable", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

        if canTip is not None:
            if canTip:
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/enable", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

            if not canTip:
                response = self.session.post(
                    f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/disable", json=data,
                    headers=self.headers(data=data))
                if json.loads(response.text)['api:statuscode'] != 0:
                    res.append(exceptions.CheckException(json.loads(response.text)))
                else:
                    res.append(json.loads(response.text)['api:statuscode'])
                    if debugs.enabled is True:
                        debugs.DebugMode(data=response.text, type="Success")

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            res.append(exceptions.CheckException(json.loads(response.text)))
        else:
            res.append(json.loads(response.text)['api:statuscode'])
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")

        return res

    # =========== TRANSFER HOST =============

    def transfer_host(self, chatId: str, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ ACCEPT HOST ==============

    def accept_host(self, chatId: str, requestId: str):
        data = json.dumps({})

        response = self.session.post(
            f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept",
            headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== KICK FROM CHAT ============

    def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        if allowRejoin: allowRejoin = 1
        if not allowRejoin: allowRejoin = 0
        response = self.session.delete(
            f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= JOIN CHAT ===============

    def join_chat(self, chatId: str, asWeb: bool = False):
        if asWeb is True:
            data = {"ndcId": "x" + self.comId, "threadId": chatId}
            response = self.session.post("https://aminoapps.com/api/join-thread", json=data, headers=self.web_headers())
            try:
                if response.json()["result"]['api:message'] == "OK":
                    return response.text
                else:
                    if self.exceptV2 is True or settings.exceptV2 is True:
                        exceptions_v2.ExceptionList(response.text)
                    else:
                        exceptions.CheckException(json.loads(response.text))
                    return response.text
            except:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

        else:
            response = self.session.post(
                f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.headers())
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return response.status_code

    # ============= LEAVE CHAT ==============

    def leave_chat(self, chatId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}",
                                       headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ DELETE CHAT ==============

    def delete_chat(self, chatId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= SUBSCRIBE ===============

    def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = json.dumps({
            "paymentContext": {
                "transactionId": transactionId,
                "isAutoRenew": autoRenew
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}/subscribe",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ PROMOTION ===============

    def promotion(self, noticeId: str, type: str = "accept"):
        response = self.session.post(f"{self.api}/x{self.comId}/s/notice/{noticeId}/{type}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== PLAY QUIZ (RAW) ============

    def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = 0):
        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============= PLAY QUIZ ===============

    def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0):
        quizAnswerList = []

        for question, answer in zip(questionIdsList, answerIdsList):
            part = json.dumps({
                "optIdList": [answer],
                "quizQuestionId": question,
                "timeSpent": 0.0
            })

            quizAnswerList.append(json.loads(part))

        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== V.C. PERMISSION =============

    def vc_permission(self, chatId: str, permission: int):
        #        Voice Chat Join Permissions
        #        1 - Open to Everyone
        #        2 - Approval Required
        #        3 - Invite Only

        data = json.dumps({
            "vvChatJoinType": permission,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== GET V.C. REP INFO ============

    def get_vc_reputation_info(self, chatId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.VcReputation(json.loads(response.text)).VcReputation

    # =========== CLAIM V.C. REP ==============

    def claim_vc_reputation(self, chatId: str):
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation",
                                     headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.VcReputation(json.loads(response.text)).VcReputation

    # =========== GET ALL USERS ==============

    def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent":
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/user-profile?type=recent&start={start}&size={size}",
                headers=self.headers())
        elif type == "banned":
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/user-profile?type=banned&start={start}&size={size}",
                headers=self.headers())
        elif type == "featured":
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}",
                headers=self.headers())
        elif type == "leaders":
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/user-profile?type=leaders&start={start}&size={size}",
                headers=self.headers())
        elif type == "curators":
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/user-profile?type=curators&start={start}&size={size}",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    # ========== GET ONLINE USERS ===========

    def get_online_users(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    # ===== GET ONLINE FAVORITE USERS =======

    def get_online_favorite_users(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    # =========== GET USER INFO ==============

    def get_user_info(self, userId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile

    # ======== GET USER FOLLOWING ==========

    def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    # ======== GET USER FOLLOWERS  ==========

    def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    # ========= GET USER VISITORS ============

    def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.VisitorsList(json.loads(response.text)).VisitorsList

    # ========= GET USER CHECK-INS ==========

    def get_user_checkins(self, userId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/check-in/stats/{userId}?timezone={-timezone // 1000}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserCheckIns(json.loads(response.text)).UserCheckIns

    # =========== GET USER BLOGS ============

    def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ========== GET USER WIKIS ==============

    def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    # ======= GET USER ACHIEVEMENTS ========

    def get_user_achievements(self, userId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/achievements",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserAchievements(json.loads(response.text)["achievements"]).UserAchievements

    # ======== GET INFLUENCER FANS ==========

    def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.InfluencerFans(json.loads(response.text)).InfluencerFans

    # ========== GET BLOCKED USERS ==========

    def get_blocked_users(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    # ========= GET BLOCKER USERS ===========

    def get_blocker_users(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)["blockerUidList"]

    # =========== SEARCH USERS==============

    def search_users(self, nickname: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    # =========== GET SAVED BLOGS ===========

    def get_saved_blogs(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/bookmark?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserSavedBlogs(json.loads(response.text)["bookmarkList"]).UserSavedBlogs

    # ======== GET LEADERBOARD INFO ========

    def get_leaderboard_info(self, type: str, start: int = 0, size: int = 25):
        if "24" in type or "hour" in type:
            response = self.session.get(
                f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=1&start={start}&size={size}",
                headers=self.headers())
        elif "7" in type or "day" in type:
            response = self.session.get(
                f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=2&start={start}&size={size}",
                headers=self.headers())
        elif "rep" in type:
            response = self.session.get(
                f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=3&start={start}&size={size}",
                headers=self.headers())
        elif "check" in type:
            response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=4",
                                        headers=self.headers())
        elif "quiz" in type:
            response = self.session.get(
                f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=5&start={start}&size={size}",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    # ============ GET WIKI INFO =============

    def get_wiki_info(self, wikiId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo

    # ======== GET RECENT WIKI ITEMS =========

    def get_recent_wiki_items(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    # ======== GET WIKI CATEGORIES ===========

    def get_wiki_categories(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item-category?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.WikiCategoryList(json.loads(response.text)["itemCategoryList"]).WikiCategoryList

    # ========= GET WIKI CATEGORY ===========

    def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item-category/{categoryId}?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.WikiCategory(json.loads(response.text)).WikiCategory

    # ========== GET TIPPED USERS ===========

    def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None,
                         chatId: str = None, start: int = 0, size: int = 25):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping/tipped-users-summary?start={start}&size={size}",
                headers=self.headers())
        elif wikiId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary?start={start}&size={size}",
                headers=self.headers())
        elif chatId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary?start={start}&size={size}",
                headers=self.headers())
        elif fileId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary?start={start}&size={size}",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.TippedUsersSummary(json.loads(response.text)).TippedUsersSummary

    # ========= GET CHAT THREADS ===========

    def get_chat_threads(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    # ======= GET PUBLIC CHAT THREADS =======

    def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    # ========== GET CHAT THREAD ============

    def get_chat_thread(self, chatId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Thread(json.loads(response.text)["thread"]).Thread

    # ======== GET CHAT MESSAGES ===========

    def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):

        #        List of Messages from an Chat.

        #        **Parameters**
        #            - **chatId** : ID of the Chat.
        #            - *size* : Size of the list.
        #            - *pageToken* : Next Page Token.

        if pageToken is not None:
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"

        response = self.session.get(url, headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.GetMessages(json.loads(response.text)).GetMessages

    # ========= GET MESSAGE INFO ============

    def get_message_info(self, chatId: str, messageId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Message(json.loads(response.text)["message"]).Message

    # =========== GET BLOG INFO ==============

    def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.headers())
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.GetBlogInfo(json.loads(response.text)).GetBlogInfo

        elif wikiId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.headers())
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo

        elif fileId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}",
                                        headers=self.headers())
            if json.loads(response.text)['api:statuscode'] != 0:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    exceptions_v2.ExceptionList(response.text)
                else:
                    exceptions.CheckException(json.loads(response.text))
                return response.text
            else:
                if debugs.enabled is True:
                    debugs.DebugMode(data=response.text, type="Success")
                return objects.SharedFolderFile(json.loads(response.text)["file"]).SharedFolderFile

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

    # ========= GET BLOG COMMENTS =========

    def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None,
                          sorting: str = "newest", start: int = 0, size: int = 25):
        if sorting == "newest":
            sorting = "newest"
        elif sorting == "oldest":
            sorting = "oldest"
        elif sorting == "top":
            sorting = "vote"

        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        elif wikiId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        elif fileId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}",
                headers=self.headers())
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()

        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    # ======== GET BLOG CATEGORIES ==========

    def get_blog_categories(self, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog-category?size={size}", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogCategoryList(json.loads(response.text)["blogCategoryList"]).BlogCategoryList

    # ======== GET BLOGS BY CATEGORY =======

    def get_blogs_by_category(self, categoryId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ========= GET QUIZ RANKINGS ===========

    def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.QuizRankings(json.loads(response.text)).QuizRankings

    # ========= GET WALL COMMENTS =========

    def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):

        #        List of Wall Comments of an User.

        #        **Parameters**
        #            - **userId** : ID of the User.
        #            - **sorting** : Order of the Comments.
        #                - ``newest``, ``oldest``, ``top``
        #            - *start* : Where to start the list.
        #            - *size* : Size of the list.

        if sorting == "newest":
            sorting = "newest"
        elif sorting == "oldest":
            sorting = "oldest"
        elif sorting == "top":
            sorting = "vote"
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        response = self.session.get(
            f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    # ========== GET RECENT BLOGS ==========

    def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
        if pageToken is not None:
            url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}"

        response = self.session.get(url, headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.RecentBlogs(json.loads(response.text)).RecentBlogs

    # =========== GET CHAT USERS ============

    def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(json.loads(response.text)["memberList"]).UserProfileList

    # ========= GET NOTIFICATIONS ===========

    def get_notifications(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.NotificationList(json.loads(response.text)["notificationList"]).NotificationList

    # ============ GET NOTICES ==============

    # TODO : Get notice to finish this
    def get_notices(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)["noticeList"]

    # ======== GET STICKER PACK INFO =========

    def get_sticker_pack_info(self, sticker_pack_id: str):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    # ========= GET STICKER PACKS ===========

    def get_sticker_packs(self):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    # ======= GET STORE CHAT BUBBLES ========

    # TODO : Finish this
    def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            response = json.loads(response.text)
            del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
            return response

    # ========= GET STORE STICKERS ==========

    # TODO : Finish this
    def get_store_stickers(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            response = json.loads(response.text)
            del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
            return response

    # ====== GET COMMUNITY STICKERS ========

    def get_community_stickers(self):
        response = self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection?type=community-shared",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.CommunityStickerCollection(json.loads(response.text)).CommunityStickerCollection

    # ======= GET STICKER COLLECTION ========

    def get_sticker_collection(self, collectionId: str):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    # ======= GET SHARED FOLDER INFO ========

    def get_shared_folder_info(self):
        response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/stats", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.GetSharedFolderInfo(json.loads(response.text)["stats"]).GetSharedFolderInfo

    # ====== GET SHARED FOLDER FILES ========

    def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.SharedFolderFileList(json.loads(response.text)["fileList"]).SharedFolderFileList

    #
    # MODERATION MENU
    #

    # ========= MODERATION HISTORY =========

    def moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None,
                           fileId: str = None, size: int = 25):
        if userId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}",
                headers=self.headers())
        elif blogId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&size={size}",
                headers=self.headers())
        elif quizId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&size={size}",
                headers=self.headers())
        elif wikiId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&size={size}",
                headers=self.headers())
        elif fileId:
            response = self.session.get(
                f"{self.api}/x{self.comId}/s/admin/operation?objectId={fileId}&objectType=109&pagingType=t&size={size}",
                headers=self.headers())
        else:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?pagingType=t&size={size}",
                                        headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.AdminLogList(json.loads(response.text)["adminLogList"]).AdminLogList

    # ============== FEATURE ===============

    def feature(self, time: int, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        if chatId:
            if time == 1: time = 3600
            if time == 1: time = 7200
            if time == 1: time = 10800

        else:
            if time == 1:
                time = 86400
            elif time == 2:
                time = 172800
            elif time == 3:
                time = 259200
            else:
                if self.exceptV2 is True or settings.exceptV2 is True:
                    return exceptions_v2.ExceptionList().wrongType()
                else:
                    raise exceptions.WrongType()

        data = {
            "adminOpName": 114,
            "adminOpValue": {
                "featuredDuration": time
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpValue"] = {"featuredType": 4}

            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif blogId:
            data["adminOpValue"] = {"featuredType": 1}

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif wikiId:
            data["adminOpValue"] = {"featuredType": 1}

            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif chatId:
            data["adminOpValue"] = {"featuredType": 5}

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin",
                                         headers=self.headers(data=data), json=data)

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ============== UNFEATURE =============

    def unfeature(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "adminOpName": 114,
            "adminOpValue": {},
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpValue"] = {"featuredType": 0}

            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif blogId:
            data["adminOpValue"] = {"featuredType": 0}

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif wikiId:
            data["adminOpValue"] = {"featuredType": 0}

            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif chatId:
            data["adminOpValue"] = {"featuredType": 0}

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin",
                                         headers=self.headers(data=data), json=data)

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================= HIDE ================

    def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None,
             fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 18

            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9

            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9

            response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin",
                                         headers=self.headers(data=data), json=data)

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================ UNHIDE ==============

    def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None,
               fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 19

            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin",
                                         headers=self.headers(data=data), json=data)

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0

            response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin",
                                         headers=self.headers(data=data), json=data)

        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().specifyType()
            else:
                raise exceptions.SpecifyType()
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ============== EDIT TITLES =============

    def edit_titles(self, userId: str, titles: list, colors: list):
        tlt = []
        for titles, colors in zip(titles, colors):
            tlt.append({"title": titles, "color": colors})

        data = json.dumps({
            "adminOpName": 207,
            "adminOpValue": {
                "titles": tlt
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================ WARN ================

    # TODO : List all warning texts
    def warn(self, userId: str, reason: str = None):
        data = json.dumps({
            "uid": userId,
            "title": "Custom",
            "content": reason,
            "attachedObject": {
                "objectId": userId,
                "objectType": 0
            },
            "penaltyType": 0,
            "adminOpNote": {},
            "noticeType": 7,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================ STRIKE ===============

    # TODO : List all strike texts
    def strike(self, userId: str, time: int, title: str = None, reason: str = None):
        if time == 1:
            time = 3600
        elif time == 2:
            time = 10800
        elif time == 3:
            time = 21600
        elif time == 4:
            time = 43200
        elif time == 5:
            time = 86400
        else:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().wrongType()
            else:
                raise exceptions.WrongType()

        data = json.dumps({
            "uid": userId,
            "title": title,
            "content": reason,
            "attachedObject": {
                "objectId": userId,
                "objectType": 0
            },
            "penaltyType": 1,
            "penaltyValue": time,
            "adminOpNote": {},
            "noticeType": 4,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================= BAN ================

    def ban(self, userId: str, reason: str, banType: int = None):
        data = json.dumps({
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/ban",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ================ UNBAN ===============

    def unban(self, userId: str, reason: str):
        data = json.dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/unban",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # ======= REORDER FEATURED USERS =======

    def reorder_featured_users(self, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/featured/reorder",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return json.loads(response.text)

    # =========== GET HIDDEN BLOGS  =========

    def get_hidden_blogs(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ========== GET FEATURED USERS =========

    def get_featured_users(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    # ======== REVIEW QUIZ QUESTIONS ========

    def review_quiz_questions(self, quizId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}?action=review", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.QuizQuestionList(json.loads(response.text)["blog"]["quizQuestionList"]).QuizQuestionList

    # =========== GET RECENT QUIZ ===========

    def get_recent_quiz(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ========== GET TRENDING QUIZ ==========

    def get_trending_quiz(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ============= GET BEST QUIZ ===========

    def get_best_quiz(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}",
                                    headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    # ============= SEND ACTION =============
    def send_action(self, actions: list, blogId: str = None, quizId: str = None, lastAction: bool = False):
        # Action List
        # Browsing

        if lastAction is True: t = 306
        else: t = 304

        data = {
            "o": {
                "actions": actions,
                "target": f"ndc://x{self.comId}/",
                "ndcId": int(self.comId),
                "params": {"topicIds": [45841, 17254, 26542, 42031, 22542, 16371, 6059, 41542, 15852]},
                "id": "831046"
            },
            "t": t
        }

        if blogId is not None or quizId is not None:
            data["target"] = f"ndc://x{self.comId}/blog/{blogId}"
            if blogId is not None: data["params"]["blogType"] = 0
            if quizId is not None: data["params"]["blogType"] = 6

        if debugs.enabled is True:  debugs.DebugMode(data=str(data), type="Info")
        return self.send(json.dumps(data))

    # ============== PURCHASE ==============

    # Provided by "spectrum#4691"
    def purchase(self, objectId: str, objectType: int, aminoPlus: bool = True, autoRenew: bool = False):
        data = {'objectId': objectId,
                'objectType': objectType,
                'v': 1,
                "timestamp": int(timestamp() * 1000)}

        if aminoPlus:
            data['paymentContext'] = {'discountStatus': 1, 'discountValue': 1, 'isAutoRenew': autoRenew}
        else:
            data['paymentContext'] = {'discountStatus': 0, 'discountValue': 1, 'isAutoRenew': autoRenew}

        response = self.session.post(f"{self.api}/x{self.comId}/s/store/purchase", headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== APPLY AVATAR FRAME ========

    # Provided by "spectrum#4691"
    def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True):
        data = {"frameId": avatarId,
                "applyToAll": 0,
                "timestamp": int(timestamp() * 1000)}

        if applyToAll: data["applyToAll"] = 1

        response = self.session.post(f"{self.api}/x{self.comId}/s/avatar-frame/apply", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= INVITE TO VOICE CHAT =========

    def invite_to_vc(self, chatId: str, userId: str):
        data = json.dumps({
            "uid": userId
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== ADD POLL OPTION ===========

    def add_poll_option(self, blogId: str, question: str):
        data = json.dumps({
            "mediaList": None,
            "title": question,
            "type": 0,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ======== CREATE WIKI CATEGORY =========

    def create_wiki_category(self, title: str, parentCategoryId: str, content: str = None):
        data = json.dumps({
            "content": content,
            "icon": None,
            "label": title,
            "mediaList": None,
            "parentCategoryId": parentCategoryId,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/item-category", headers=self.headers(data=data),
                                     json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ======== CREATE SHARED FOLDER ========

    def create_shared_folder(self, title: str):
        data = json.dumps({
            "title": title,
            "timestamp": int(timestamp() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/folders",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ SUBMIT TO WIKI ============

    def submit_to_wiki(self, wikiId: str, message: str):
        data = json.dumps({
            "message": message,
            "itemId": wikiId,
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= ACCEPT WIKI REQUEST =========

    def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list):
        data = json.dumps({
            "destinationCategoryIdList": destinationCategoryIdList,
            "actionType": "create",
            "timestamp": int(timestamp() * 1000)
        })

        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/approve",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= REJECT WIKI REQUEST =========

    def reject_wiki_request(self, requestId: str):
        data = json.dumps({})

        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/reject",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= GET WIKI SUBMISSIONS ========

    def get_wiki_submissions(self, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.WikiRequestList(json.loads(response.text)["knowledgeBaseRequestList"]).WikiRequestList

    # ============ GET LIVE LAYER ============

    def get_live_layer(self):
        response = self.session.get(f"{self.api}/x{self.comId}/s/live-layer/homepage?v=2", headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.LiveLayer(json.loads(response.text)["liveLayerList"]).LiveLayer

    # ============ GET BLOG USERS ===========

    def get_blog_users(self, blogId: str, start: int = 0, size: int = 25):
        response = self.session.get(
            f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic%3Ax{self.comId}%3Ausers-browsing-blog-at%3A{blogId}&start={start}&size={size}",
            headers=self.headers())
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    # ============= APPLY BUBBLE ===========
    # By Romanok2805

    def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False) -> objects.Bubble:
        data = {
            "applyToAll": 0,
            "bubbleId": bubbleId,
            "threadId": chatId,
            "timestamp": int(timestamp() * 1000)
        }

        if applyToAll is True:
            data["applyToAll"] = 1

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/apply-bubble",
                                     headers=self.headers(data=data), json=data)
        if json.loads(response.text)['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== DELETE CHAT BUBBLE ==========

    def delete_chat_bubble(self, bubbleId: str):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}",
                                       headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ======== UPLOAD CUSTOM BUBBLE =========

    def upload_custom_bubble(self, templateId: str, bubble: BinaryIO):
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/templates/{templateId}/generate",
                                     headers=self.headers(), data=bubble)
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.text

    # ============ GET BUBBLE INFO ===========
    # By Romanok2805

    def get_bubble_info(self, bubbleId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}", headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Bubble(json.loads(response.text)["chatBubble"]).Bubble

    # ======= GET BUBBLE TEMPLATE LIST =======
    # By Romanok2805

    def get_bubble_template_list(self, start: int = 0, size: int = 25) -> objects.BubbleList:
        """
        Get a list of bubble templates that can be customized
        **Returns**
            - **Success** : BubbleList object
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/chat-bubble/templates?start={start}&size={size}",
                                    headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BubbleList(json.loads(response.text)["templateList"]).BubbleList

    # ========== GET OWN BUBBLE LIST =========
    # By Romanok2805

    def get_own_bubble_list(self, threadId: str = None, type: str = "current-community", start: int = 0,
                            size: int = 20) -> objects.BubbleList:
        """
        Get a list of bubbles that are on the account
        **Parameters**
            - **threadId** : id of thread (optional)
            - **type** : `current-community` for local or `all` for all bubbles
        **Returns**
            - **Success** : BubbleList object
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        params = {
            "type": type,
            "start": start,
            "size": size
        }

        if threadId:
            params["threadId"] = threadId

        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/chat-bubble", headers=self.headers(), data=params)
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.BubbleList(json.loads(response.text)["chatBubbleList"]).BubbleList

    # ===== CREATE BUBBLE FROM TEMPLATE =====
    # By Romanok2805

    def create_bubble_from_template(self, templateId: str = "949156e1-cc43-49f0-b9cf-3bbbb606ad6e",
                                    bubble_zip: BinaryIO = None) -> objects.Bubble:  # Spring bubbleId

        if bubble_zip is None:
            bubble_zip = self.generate_bubble()
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/templates/{templateId}/generate",
                                     headers=self.headers(), data=bubble_zip.read())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Bubble(json.loads(response.text)["chatBubble"]).Bubble

    # ======== UPDATE CUSTOM BUBBLE ========
    # By Romanok2805

    def update_custom_bubble(self, bubbleId: str, bubble_zip: BinaryIO = None) -> objects.Bubble:
        if bubble_zip is None:
            bubble_zip = self.generate_bubble()
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}", headers=self.headers(),
                                     data=bubble_zip.read())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Bubble(json.loads(response.text)["chatBubble"]).Bubble

    # ========== DEACTIVATE BUBBLE ==========
    # By Romanok2805

    def deactivate_bubble(self, bubbleId: str) -> int:
        """
        Deactivates the visibility of the bubble for this community
        **Parameters**
            - **bubbleId** : id of bubble
        **Returns**
            - **Success** : 200 (int)
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}/deactivate",
                                     headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ ACTIVATE BUBBLE ==========
    # By Romanok2805

    def activate_bubble(self, bubbleId: str) -> int:
        """
        Activates the visibility of the bubble for this community
        **Parameters**
            - **bubbleId** : id of bubble
        **Returns**
            - **Success** : 200 (int)
            - **Fail** : :meth:`Exceptions <amino.lib.src.exceptions>`
        """

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}/activate",
                                     headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== GET VIDEO REP INFO ============
    # By SirLez & Bovonos

    def get_video_rep_info(self, chatId: str):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation",
                                    headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.RepInfo(json.loads(response.text)).RepInfo

    # ============ CLAIM VIDEO REP ==============
    # By SirLez & Bovonos

    def claim_video_rep(self, chatId: str):
        info = self.get_video_rep_info(chatId)
        reputation = info.json["reputation"]

        if int(reputation) < 1:
            if self.exceptV2 is True or settings.exceptV2 is True:
                return exceptions_v2.ExceptionList().cannotNotClaimReputation()
            else:
                raise exceptions.CannotNotClaimReputation()

        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation",
                                     headers=self.headers())
        if response.status_code != 200:
            if self.exceptV2 is True or settings.exceptV2 is True:
                exceptions_v2.ExceptionList(response.text)
            else:
                exceptions.CheckException(json.loads(response.text))
            return response.text
        else:
            if debugs.enabled is True:
                debugs.DebugMode(data=response.text, type="Success")
            return objects.Rep(json.loads(response.text)).Rep
