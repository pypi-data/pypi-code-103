import requests
from time import time as timestamp
from typing import BinaryIO

from . import client, settings
from .src import exceptions, exceptions_v2, objects, debugs


# =========== ACM CLASS BELOW ===========
class ACM(client.Client):
    def __init__(self, profile: objects.UserProfile, comId: str = None):
        client.Client.__init__(self)

        self.profile = profile
        self.comId = comId

    # ========== CREATE COMMUNITY ==========
    # TODO : Finish the imaging sizing, might not work for every picture...
    def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = 0, primaryLanguage: str = "en"):
        data = {
            "icon": {
                "height": 512.0,
                "imageMatrix": [1.6875, 0.0, 108.0, 0.0, 1.6875, 497.0, 0.0, 0.0, 1.0],
                "path": self.upload_media(icon, "image"),
                "width": 512.0,
                "x": 0.0,
                "y": 0.0
            },
            "joinType": joinType,
            "name": name,
            "primaryLanguage": primaryLanguage,
            "tagline": tagline,
            "templateId": 9,
            "themeColor": themeColor,
            "timestamp": int(timestamp() * 1000)
        }

        response = self.session.post(f"{self.api}/g/s/community", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== DELETE COMMUNITY ===========
    def delete_community(self, email: str, password: str, verificationCode: str):
        data = {
            "secret": f"0 {password}",
            "validationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email
            },
            "deviceID": self.deviceId()
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/g/s-x{self.comId}/community/delete-request", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== LIST COMMUNITIES ===========
    def list_communities(self, start: int = 0, size: int = 25):
        response = self.session.get(f"{self.api}/g/s/community/managed?start={start}&size={size}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return objects.CommunityList(response.json()["communityList"]).CommunityList

    # ============ GET CATEGORIES ============
    def get_categories(self, start: int = 0, size: int = 25):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog-category?start={start}&size={size}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.json()

    # ======= CHANGE SIDEPANEL COLOR ========
    def change_sidepanel_color(self, color: str):
        data = {
            "path": "appearance.leftSidePanel.style.iconColor",
            "value": color,
            "timestamp": int(timestamp() * 1000)
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.json()

    # ======= UPLOAD THEMEPACK [ RAW ] =======
    def upload_themepack_raw(self, file: BinaryIO):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/media/upload/target/community-theme-pack", data=file.read(), headers=self.headers(data=file.read()))
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.json()

    # ============== PROMOTE ===============
    def promote(self, userId: str, rank: str):
        rank = rank.lower().replace("agent", "transfer-agent")

        if rank.lower() not in ["transfer-agent", "leader", "curator"]:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().wrongType()
            else: raise exceptions.WrongType(rank)

        data = {}

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{rank}", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== GET JOIN REQUESTS ===========
    def get_join_requests(self, start: int = 0, size: int = 25):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()

        response = self.session.get(f"{self.api}/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return objects.JoinRequest(response.json()).JoinRequest

    # ========= ACCEPT JOIN REQUEST =========
    def accept_join_request(self, userId: str):
        data = {}

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/accept", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========= REJECT JOIN REQUEST ==========
    def reject_join_request(self, userId: str):
        data = {}

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/reject", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ======== GET COMMUNITY STATS =========
    def get_community_stats(self):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()

        response = self.session.get(f"{self.api}/x{self.comId}/s/community/stats", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return objects.CommunityStats(response.json()["communityStats"]).CommunityStats

    # ====== GET COMMUNITY USER STATS =======
    def get_community_user_stats(self, type: str, start: int = 0, size: int = 25):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()

        if type.lower() == "leader": target = "leader"
        elif type.lower() == "curator": target = "curator"
        else: 
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().wrongType()
            else: raise exceptions.WrongType(type)

        response = self.session.get(f"{self.api}/x{self.comId}/s/community/stats/moderation?type={target}&start={start}&size={size}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return objects.UserProfileList(response.json()["userProfileList"]).UserProfileList

    # ====== CHANGE WELCOME MESSAGE ========
    def change_welcome_message(self, message: str, isEnabled: bool = True):
        data = {
            "path": "general.welcomeMessage",
            "value": {
                "enabled": isEnabled,
                "text": message
            },
            "timestamp": int(timestamp() * 1000)
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True:  debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== CHANGE GUIDELINES =========
    def change_guidelines(self, message: str):
        data = {
            "content": message,
            "timestamp": int(timestamp() * 1000)
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/guideline", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== EDIT COMMUNITY ============
    def edit_community(self, name: str = None, description: str = None, aminoId: str = None, primaryLanguage: str = None, themePackUrl: str = None):
        data = {"timestamp": int(timestamp() * 1000)}

        if name is not None: data["name"] = name
        if description is not None: data["content"] = description
        if aminoId is not None: data["endpoint"] = aminoId
        if primaryLanguage is not None: data["primaryLanguage"] = primaryLanguage
        if themePackUrl is not None: data["themePackUrl"] = themePackUrl

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/settings", json=data, headers=self.headers(data=data))
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # =========== CHANGE MODULE ============
    def change_module(self, module: str, isEnabled: bool):
        if module.lower() == "chat": mod = "module.chat.enabled"
        elif module.lower() == "livechat": mod = "module.chat.avChat.videoEnabled"
        elif module.lower() == "screeningroom": mod = "module.chat.avChat.screeningRoomEnabled"
        elif module.lower() == "publicchats": mod = "module.chat.publicChat.enabled"
        elif module.lower() == "posts": mod = "module.post.enabled"
        elif module.lower() == "ranking": mod = "module.ranking.enabled"
        elif module.lower() == "leaderboards": mod = "module.ranking.leaderboardEnabled"
        elif module.lower() == "featured": mod = "module.featured.enabled"
        elif module.lower() == "featuredposts": mod = "module.featured.postEnabled"
        elif module.lower() == "featuredusers": mod = "module.featured.memberEnabled"
        elif module.lower() == "featuredchats": mod = "module.featured.publicChatRoomEnabled"
        elif module.lower() == "sharedfolder": mod = "module.sharedFolder.enabled"
        elif module.lower() == "influencer": mod = "module.influencer.enabled"
        elif module.lower() == "catalog": mod = "module.catalog.enabled"
        elif module.lower() == "externalcontent": mod = "module.externalContent.enabled"
        elif module.lower() == "topiccategories": mod = "module.topicCategories.enabled"
        else:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().specifyType()
            else: raise exceptions.SpecifyType()

        data = {
            "path": mod,
            "value": isEnabled,
            "timestamp": int(timestamp() * 1000)
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ ADD INFLUENCER ===========
    def add_influencer(self, userId: str, monthlyFee: int):
        data = {
            "monthlyFee": monthlyFee,
            "timestamp": int(timestamp() * 1000)
        }

        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.headers(data=data), json=data)
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ========== REMOVE INFLUENCER =========
    def remove_influencer(self, userId: str):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = requests.delete(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code

    # ============ GET NOTICE LIST ===========
    def get_notice_list(self, start: int = 0, size: int = 25):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: 
                debugs.DebugMode(data=response.text, type="Success")
            return objects.NoticeList(response.json()["noticeList"]).NoticeList

    # ======== DELETE PENDING ROLES =========
    def delete_pending_role(self, noticeId: str):
        if self.comId is None:
            if self.exceptV2 is True or settings.exceptV2 is True: return exceptions_v2.ExceptionList().communityNeeded()
            else: raise exceptions.CommunityNeeded()
        response = requests.delete(f"{self.api}/x{self.comId}/s/notice/{noticeId}", headers=self.headers())
        if response.json()['api:statuscode'] != 0:
            if self.exceptV2 is True or settings.exceptV2 is True: exceptions_v2.ExceptionList(response.text)
            else: exceptions.CheckException(response.json())
            return response.text
        else:
            if debugs.enabled is True: debugs.DebugMode(data=response.text, type="Success")
            return response.status_code
