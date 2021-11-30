from inspect import getframeinfo, stack
from hcl import settings
import json
import time
import os

# Call example for detector: exceptions.ExceptionList(data=response.text)
# Call example for manual trigger: exceptions.ExceptionList().exception

# ========== EXCEPTIONS BELOW===========

class ExceptionList:
    def colored(self, r, g, b, text, rb : int = None, gb : int = None, bb : int = None):
    # print(colored(200, 20, 200, 0, 0, 0, "Hello World"))
        if rb is None and gb is None and bb is None:
            return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)
        else:
            return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m{}\033[0m".format(r, g, b, rb, gb, bb, text)

    def __init__(self, data : str = None):
        self.caller = getframeinfo(stack()[2][0])
        if data == None:
            data = "API Found no displayable data for this exception."
            self.data = data
            self.statuscode = None
        else:
            self.data = data
            try:
                self.statuscode =  json.loads(data)["api:statuscode"]
            except:
                self.statuscode = None

# ========== EXCEPTION PARSER ===========

            if self.statuscode == 100: self.unsupportedService()
            elif self.statuscode == 102: self.fileTooLarge()
            elif self.statuscode == 103 or self.statuscode == 104: self.invalidRequest()
            elif self.statuscode == 105: self.invalidSession()
            elif self.statuscode == 106: self.accessDenied()
            elif self.statuscode == 107: self.unexistentData()
            elif self.statuscode == 110: self.actionNotAllowed()
            elif self.statuscode == 111: self.serviceUnderMaintenance()
            elif self.statuscode == 113: self.messageNeeded()
            elif self.statuscode == 200: self.invalidAccountOrPassword()
            elif self.statuscode == 201: self.accountDisabled()
            elif self.statuscode == 210: self.accountDisabled()
            elif self.statuscode == 213: self.invalidEmail()
            elif self.statuscode == 214: self.invalidPassword()
            elif self.statuscode == 215: self.emailAlreadyTaken_or_unsupportedEmail()
            elif self.statuscode == 216: self.accountDoesntExist()
            elif self.statuscode == 218: self.invalidDevice()
            elif self.statuscode == 219: self.accountLimitReached_or_tooManyRequests()
            elif self.statuscode == 221: self.cantFollowYourself()
            elif self.statuscode == 225: self.userUnavailable()
            elif self.statuscode == 229: self.youAreBanned()
            elif self.statuscode == 230: self.userNotMemberOfCommunity()
            elif self.statuscode == 235: self.requestRejected()
            elif self.statuscode == 238: self.activateAccount()
            elif self.statuscode == 239: self.cantLeaveCommunity()
            elif self.statuscode == 240: self.reachedTitleLength()
            elif self.statuscode == 241: self.emailFlaggedAsSpam()
            elif self.statuscode == 246: accountDeleted()
            elif self.statuscode == 251: self.API_ERR_EMAIL_NO_PASSWORD()
            elif self.statuscode == 257: self.API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY()
            elif self.statuscode == 262: self.reachedMaxTitles()
            elif self.statuscode == 270: self.verificationRequired()
            elif self.statuscode == 271: self.API_ERR_INVALID_AUTH_NEW_DEVICE_LINK()
            elif self.statuscode == 291: self.commandCooldown()
            elif self.statuscode == 293: self.userBannedByTeamAmino()
            elif self.statuscode == 300: self.badImage()
            elif self.statuscode == 313: self.invalidThemepack()
            elif self.statuscode == 314: self.invalidVoiceNote()
            elif self.statuscode == 500 or self.statuscode == 700 or self.statuscode == 1600: self.requestedNoLongerExists()
            elif self.statuscode == 503: self.pageRepostedTooRecently()
            elif self.statuscode == 551: self.insufficientLevel()
            elif self.statuscode == 702: self.wallCommentingDisabled()
            elif self.statuscode == 801: self.communityNoLongerExists()
            elif self.statuscode == 802: self.invalidCodeOrLink()
            elif self.statuscode == 805: self.communityNameAlreadyTaken()
            elif self.statuscode == 806: self.communityCreateLimitReached()
            elif self.statuscode == 814: self.communityDisabled()
            elif self.statuscode == 833: self.communityDeleted()
            elif self.statuscode == 1002: self.reachedMaxCategories()
            elif self.statuscode == 1501: self.duplicatePollOption()
            elif self.statuscode == 1507: self.reachedMaxPollOptions()
            elif self.statuscode == 1602: self.tooManyChats()
            elif self.statuscode == 1605: self.chatFull()
            elif self.statuscode == 1606: self.tooManyInviteUsers()
            elif self.statuscode == 1611: self.chatInvitesDisabled()
            elif self.statuscode == 1612: self.removedFromChat()
            elif self.statuscode == 1613: self.userNotJoined()
            elif self.statuscode == 1627: self.API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS()
            elif self.statuscode == 1637: self.memberKickedByOrganizer()
            elif self.statuscode == 1661: self.levelFiveRequiredToEnableProps()
            elif self.statuscode == 1663: self.chatViewOnly()
            elif self.statuscode == 1664: self.chatMessageTooBig()
            elif self.statuscode == 1900: self.inviteCodeNotFound()
            elif self.statuscode == 2001: self.alreadyRequestedJoinCommunity()
            elif self.statuscode == 2501: self.API_ERR_PUSH_SERVER_LIMITATION_APART()
            elif self.statuscode == 2502: self.API_ERR_PUSH_SERVER_LIMITATION_COUNT()
            elif self.statuscode == 2503: self.API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY()
            elif self.statuscode == 2504: self.API_ERR_PUSH_SERVER_LIMITATION_TIME()
            elif self.statuscode == 2601: self.alreadyCheckedIn()
            elif self.statuscode == 2611: self.alreadyUsedMonthlyRepair()
            elif self.statuscode == 2800: self.accountAlreadyRestored()
            elif self.statuscode == 3102: self.incorrectVerificationCode()
            elif self.statuscode == 3905: self.notOwnerOfChatBubble()
            elif self.statuscode == 4300: self.notEnoughCoins()
            elif self.statuscode == 4400: self.alreadyPlayedLottery()
            elif self.statuscode == 4500: self.cannotSendCoins()
            elif self.statuscode == 4501: self.cannotSendCoins()
            elif self.statuscode == 6001: self.aminoIDAlreadyChanged()
            elif self.statuscode == 6002: self.invalidAminoID()
            elif self.statuscode == 9901: self.invalidName()
            else: self.unknownException()

# ========== EXCEPTION PRINTER===========

    def printException(self, exception, message, string):
        callercontext = (self.caller.code_context[0]).replace('\n', '')
        print("\n" + self.colored(0, 0, 0, rb=244, gb=67, bb=54, text=f" ❮ {exception} ❯ ") + self.colored(255, 138, 138, rb=36, gb=36, bb=36, text=f" {self.caller.filename}, Line = {self.caller.lineno}"))
        print(self.colored(0, 0, 0, rb=244, gb=67, bb=54, text=" FUNCTION     ❯ ") + self.colored(244, 67, 54, f" {callercontext}"))
        print(self.colored(0, 0, 0, rb=244, gb=67, bb=54, text=" API CODE     ❯ ") + self.colored(244, 67, 54, f" {self.statuscode}"))
        print(self.colored(0, 0, 0, rb=244, gb=67, bb=54, text=" API MESSAGE  ❯ ") + self.colored(244, 67, 54, f" {message}"))
        print(self.colored(0, 0, 0, rb=244, gb=67, bb=54, text=" API STRING   ❯ ") + self.colored(244, 66, 54, f" {string}"))
        print(self.colored(255, 138, 138, rb=36, gb=36, bb=36, text=f" {self.data}") + "\n")
        if settings.eV2Timer == True:
            wait = settings.eV2TimerDuration
            print(self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=f" ❮ Warning ❯ ") + self.colored(255, 185, 52, f" The api will continue running in: T-{settings.eV2TimerDuration} Seconds.") + "\n" + self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=" ❯ ") + self.colored(255, 185, 52, " Press ctrl + c to stop.") + "\n")
            while wait:
                try:
                    mins, secs = divmod(wait, 60) 
                    timer = '{:02d}:{:02d}'.format(mins, secs)
                    time.sleep(1) 
                    wait -= 1
                    print(self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=f" Countdown ❯ ") + self.colored(255, 185, 52, f" {timer}"), end='\r')
                except KeyboardInterrupt:
                    os._exit(1)
                pass
            print("\n")

# ======== AMINO API EXCEPTIONS =========

    def unsupportedService(self):
        exception = "UnsupportedService"
        message = "Unsupported service. Your client may be out of date. Please update it to the latest version."
        string = "Unknown String"
        self.printException(exception, message, string)

    def fileTooLarge(self):
        exception = "FileTooLarge"
        message = "Unknown Message"
        string = "API_STD_ERR_ENTITY_TOO_LARGE_RAW"
        self.printException(exception, message, string)

    def invalidRequest(self):
        exception = "InvalidRequest"
        message = "Invalid Request. Please update to the latest version. If the problem continues, please contact us."
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidSession(self):
        exception = "InvalidSession"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def accessDenied(self):
        exception = "AccessDenied"
        message = "Access denied."
        string = "Unknown String"
        self.printException(exception, message, string)

    def unexistentData(self):
        exception = "UnexistentData"
        message = "The requested data does not exist."
        string = "Unknown String"
        self.printException(exception, message, string)

    def actionNotAllowed(self):
        exception = "ActionNotAllowed"
        message = "Action not allowed."
        string = "Unknown String"
        self.printException(exception, message, string)

    def serviceUnderMaintenance(self):
        exception = "ServiceUnderMaintenance"
        message = "Sorry, this service is under maintenance. Please check back later."
        string = "Unknown String"
        self.printException(exception, message, string)

    def messageNeeded(self):
        exception = "MessageNeeded"
        message = "Be more specific, please."
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidAccountOrPassword(self):
        exception = "InvalidAccountOrPassword"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def accountDisabled(self):
        exception = "AccountDisabled"
        message = "This account is disabled."
        string = "AUTH_DISABLED_ACCOUNT"
        self.printException(exception, message, string)

    def invalidEmail(self):
        exception = "InvalidEmail"
        message = "Invalid email address."
        string = "API_ERR_EMAIL"
        self.printException(exception, message, string)

    def invalidPassword(self):
        exception = "InvalidPassword"
        message = "Invalid password. Password must be 6 characters or more and contain no spaces."
        string = "API_ERR_PASSWORD"
        self.printException(exception, message, string)

    def emailAlreadyTaken_or_unsupportedEmail(self):
        exception = "EmailAlreadyTaken or UnsupportedEmail"
        message = "EmailAlreadyTaken: Hey this email ``X`` has been registered already. You can try to log in with the email or edit the email. | Unsupported Email: This email address is not supported."
        string = "API_ERR_EMAIL_TAKEN or "
        self.printException(exception, message, string)

    def accountDoesntExist(self):
        exception = "AccountDoesntExist"
        message = "Unknown Message"
        string = "AUTH_ACCOUNT_NOT_EXISTS"
        self.printException(exception, message, string)

    def invalidDevice(self):
        exception = "InvalidDevice"
        message = "Error! Your device is currently not supported, or the app is out of date. Please update to the latest version."
        string = "Unknown String"
        self.printException(exception, message, string)

    def accountLimitReached_or_tooManyRequests(self):
        exception = "AccountLimitReached or TooManyRequests"
        message = "AccountLimitReached: A maximum of 3 accounts can be created from this device. If you forget your password, please reset it. | TooManyRequests: Too many requests. Try again later."
        string = "Unknown String"
        self.printException(exception, message, string)

    def cantFollowYourself(self):
        exception = "CantFollowYourself"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def userUnavailable(self):
        exception = "UserUnavailable"
        message = "This user is unavailable."
        string = "Unknown String"
        self.printException(exception, message, string)

    def youAreBanned(self):
        exception = "YouAreBanned"
        message = "You are banned."
        string = "Unknown String"
        self.printException(exception, message, string)

    def userNotMemberOfCommunity(self):
        exception = "UserNotMemberOfCommunity"
        message = "You have to join this Community first."
        string = "API_ERR_USER_NOT_IN_COMMUNITY"
        self.printException(exception, message, string)

    def requestRejected(self):
        exception = "RequestRejected"
        message = "Request rejected. You have been temporarily muted (read only mode) because you have received a strike. To learn more, please check the Help Center."
        string = "Unknown String"
        self.printException(exception, message, string)

    def activateAccount(self):
        exception = "ActivateAccount"
        message = "Please activate your account first. Check your email, including your spam folder."
        string = "Unknown String"
        self.printException(exception, message, string)

    def cantLeaveCommunity(self):
        exception = "CantLeaveCommunity"
        message = "Sorry, you can not do this before transferring your Agent status to another member."
        string = "Unknown String"
        self.printException(exception, message, string)

    def reachedTitleLength(self):
        exception = "ReachedTitleLength"
        message = "Sorry, the max length of member's title is limited to 20."
        string = "Unknown String"
        self.printException(exception, message, string)

    def emailFlaggedAsSpam(self):
        exception = "EmailFlaggedAsSpam"
        message = "This email provider has been flagged for use in spamming."
        string = "Unknown String"
        self.printException(exception, message, string)

    def accountDeleted(self):
        exception = "AccountDeleted"
        message = "Unknown Message"
        string = "AUTH_RECOVERABLE_DELETED_ACCOUNT"
        self.printException(exception, message, string)

    def API_ERR_EMAIL_NO_PASSWORD(self):
        exception = "API_ERR_EMAIL_NO_PASSWORD"
        message = "Unknown Message"
        string = "API_ERR_EMAIL_NO_PASSWORD"
        self.printException(exception, message, string)

    def API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY(self):
        exception = "API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY"
        message = "Unknown Message"
        string = "API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY"
        self.printException(exception, message, string)

    def reachedMaxTitles(self):
        exception = "ReachedMaxTitles"
        message = "You can only add up to 20 Titles. Please choose the most relevant ones."
        string = "Unknown String"
        self.printException(exception, message, string)

    def verificationRequired(self):
        exception = "VerificationRequired"
        message = "Verification Required."
        string = "API_ERR_NEED_TWO_FACTOR_AUTHENTICATION"
        self.printException(exception, message, string)

    def API_ERR_INVALID_AUTH_NEW_DEVICE_LINK(self):
        exception = "API_ERR_INVALID_AUTH_NEW_DEVICE_LINK"
        message = "Unknown Message"
        string = "API_ERR_INVALID_AUTH_NEW_DEVICE_LINK"
        self.printException(exception, message, string)

    def commandCooldown(self):
        exception = "CommandCooldown"
        message = "Whoa there! You've done too much too quickly. Take a break and try again later."
        string = "Unknown String"
        self.printException(exception, message, string)

    def userBannedByTeamAmino(self):
        exception = "UserBannedByTeamAmino"
        message = "Sorry, this user has been banned by Team Amino."
        string = "Unknown String"
        self.printException(exception, message, string)

    def badImage(self):
        exception = "BadImage"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidThemepack(self):
        exception = "InvalidThemepack"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidVoiceNote(self):
        exception = "InvalidVoiceNote"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def requestedNoLongerExists(self):
        exception = "RequestedNoLongerExists"
        message = "Sorry, the requested data no longer exists. Try refreshing the view."
        string = "Unknown String"
        self.printException(exception, message, string)

    def pageRepostedTooRecently(self):
        exception = "PageRepostedTooRecently"
        message = "Sorry, you have reported this page too recently."
        string = "Unknown String"
        self.printException(exception, message, string)

    def insufficientLevel(self):
        exception = "InsufficientLevel"
        message = "This post type is restricted to members with a level ``X`` ranking and above."
        string = "Unknown String"
        self.printException(exception, message, string)

    def wallCommentingDisabled(self):
        exception = "WallCommentingDisabled"
        message = "This member has disabled commenting on their wall."
        string = "Unknown String"
        self.printException(exception, message, string)

    def communityNoLongerExists(self):
        exception = "CommunityNoLongerExists"
        message = "This Community no longer exists."
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidCodeOrLink(self):
        exception = "InvalidCodeOrLink"
        message = "Sorry, this code or link is invalid."
        string = "Unknown String"
        self.printException(exception, message, string)

    def communityNameAlreadyTaken(self):
        exception = "CommunityNameAlreadyTaken"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def communityCreateLimitReached(self):
        exception = "CommunityCreateLimitReached"
        message = "Unknown Message"
        string = "API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_EXCEED_QUOTA"
        self.printException(exception, message, string)

    def communityDisabled(self):
        exception = "CommunityDisabled"
        message = "This Community is disabled."
        string = "Unknown String"
        self.printException(exception, message, string)

    def communityDeleted(self):
        exception = "CommunityDeleted"
        message = "This Community has been deleted."
        string = "Unknown String"
        self.printException(exception, message, string)

    def reachedMaxCategories(self): # by ssilc1111
        exception = "ReachedMaxCategories"
        message = "Sorry, you can create up to 100 categories."
        string = "Unknown String"
        self.printException(exception, message, string)

    def duplicatePollOption(self):
        exception = "DuplicatePollOption"
        message = "Sorry, you have duplicate poll options."
        string = "Unknown String"
        self.printException(exception, message, string)

    def reachedMaxPollOptions(self):
        exception = "DuplicatePollOption"
        message = "Sorry, you can only join or add up to 5 of your items per poll."
        string = "Unknown String"
        self.printException(exception, message, string)

    def tooManyChats(self):
        exception = "TooManyChats"
        message = "Sorry, you can only have up to 1000 chat sessions."
        string = "Unknown String"
        self.printException(exception, message, string)

    def chatFull(self):
        exception = "ChatFull"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def tooManyInviteUsers(self):
        exception = "TooManyInviteUsers"
        message = "Sorry, you can only invite up to 999 people."
        string = "Unknown String"
        self.printException(exception, message, string)

    def chatInvitesDisabled(self):
        exception = "ChatInvitesDisabled"
        message = "This user has disabled chat invite requests."
        string = "Unknown String"
        self.printException(exception, message, string)

    def removedFromChat(self):
        exception = "RemovedFromChat"
        message = "You've been removed from this chatroom."
        string = "Unknown String"
        self.printException(exception, message, string)

    def userNotJoined(self):
        exception = "UserNotJoined"
        message = "Sorry, this user has not joined."
        string = "Unknown String"
        self.printException(exception, message, string)

    def API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS(self):
        exception = "API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS"
        message = "Unknown Message"
        string = "API_ERR_CHAT_VVCHAT_NO_MORE_REPUTATIONS"
        self.printException(exception, message, string)

    def memberKickedByOrganizer(self):
        exception = "MemberKickedByOrganizer"
        message = "This member was previously kicked by the organizer and cannot be reinvited."
        string = "Unknown String"
        self.printException(exception, message, string)

    def levelFiveRequiredToEnableProps(self):
        exception = "LevelFiveRequiredToEnableProps"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def chatViewOnly(self):
        exception = "ChatViewOnly"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def chatMessageTooBig(self):
        exception = "ChatMessageTooBig"
        message = "Unknown Message"
        string = "API_ERR_CHAT_MESSAGE_CONTENT_TOO_LONG"
        self.printException(exception, message, string)

    def inviteCodeNotFound(self):
        exception = "InviteCodeNotFound"
        message = "Sorry, the requested data no longer exists. Try refreshing the view."
        string = "Unknown String"
        self.printException(exception, message, string)

    def alreadyRequestedJoinCommunity(self):
        exception = "AlreadyRequestedJoinCommunity"
        message = "Sorry, you have already submitted a membership request."
        string = "Unknown String"
        self.printException(exception, message, string)

    def API_ERR_PUSH_SERVER_LIMITATION_APART(self):
        exception = "API_ERR_PUSH_SERVER_LIMITATION_APART"
        message = "Unknown Message"
        string = "API_ERR_PUSH_SERVER_LIMITATION_APART"
        self.printException(exception, message, string)

    def API_ERR_PUSH_SERVER_LIMITATION_COUNT(self):
        exception = "API_ERR_PUSH_SERVER_LIMITATION_COUNT"
        message = "Unknown Message"
        string = "API_ERR_PUSH_SERVER_LIMITATION_COUNT"
        self.printException(exception, message, string)

    def API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY(self):
        exception = "API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY"
        message = "Unknown Message"
        string = "API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY"
        self.printException(exception, message, string)

    def API_ERR_PUSH_SERVER_LIMITATION_TIME(self):
        exception = "API_ERR_PUSH_SERVER_LIMITATION_TIME"
        message = "Unknown Message"
        string = "API_ERR_PUSH_SERVER_LIMITATION_TIME"
        self.printException(exception, message, string)

    def alreadyCheckedIn(self):
        exception = "AlreadyCheckedIn"
        message = "Sorry, you can't check in any more."
        string = "Unknown String"
        self.printException(exception, message, string)

    def alreadyUsedMonthlyRepair(self):
        exception = "AlreadyUsedMonthlyRepair"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def accountAlreadyRestored(self):
        exception = "AccountAlreadyRestored"
        message = "Account already restored."
        string = "Unknown String"
        self.printException(exception, message, string)

    def incorrectVerificationCode(self):
        exception = "IncorrectVerificationCode"
        message = "Incorrect verification code."
        string = "Unknown String"
        self.printException(exception, message, string)

    def notOwnerOfChatBubble(self):
        exception = "NotOwnerOfChatBubble"
        message = "You are not the owner of this chat bubble."
        string = "Unknown String"
        self.printException(exception, message, string)

    def notEnoughCoins(self):
        exception = "NotEnoughCoins"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def alreadyPlayedLottery(self):
        exception = "AlreadyPlayedLottery"
        message = "You have played the maximum number of lucky draws."
        string = "Unknown String"
        self.printException(exception, message, string)

    def cannotSendCoins(self):
        exception = "CannotSendCoins"
        message = "Unknown Message"
        string = "Unknown String"
        self.printException(exception, message, string)

    def aminoIDAlreadyChanged(self):
        exception = "AminoIDAlreadyChanged"
        message = "Amino ID cannot be changed after you set it."
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidAminoID(self):
        exception = "InvalidAminoID"
        message = "Invalid Amino ID"
        string = "Unknown String"
        self.printException(exception, message, string)

    def invalidName(self):
        exception = "InvalidName"
        message = "Sorry, the name is invalid."
        string = "Unknown String"
        self.printException(exception, message, string)


# ======== HCL LIBRARY EXCEPTIONS ========


    def specifyType(self):
        exception = "SpecifyType"
        message = "Triggered when you need to specify the output of the command."
        string = "HCL_SPECIFY_TYPE"
        self.printException(exception, message, string)

    def cannotNotClaimReputation(self):
        exception = "CannotNotClaimReputation"
        message = "Reputation to be claimed should be higher than 1"
        string = "HCL_CANNOT_CLAIM_REP"
        self.printException(exception, message, string)

    def wrongType(self):
        exception = "WrongType"
        message = "Triggered when you attribute the function the wrong type."
        string = "HCL_WRONG_TYPE"
        self.printException(exception, message, string)

    def unknownResponse(self):
        exception = "UnknownResponse"
        message = "Triggered when an error occurs but the reason is unknown."
        string = "HCL_UNKNOWN_RESPONSE"
        self.printException(exception, message, string)

    def notLoggedIn(self):
        exception = "NotLoggedIn"
        message = "Triggered when you try to make an action but you aren't logged in."
        string = "HCL_NOT_LOGGED_IN"
        self.printException(exception, message, string)

    def noCommunity(self):
        exception = "NoCommunity"
        message = "Triggered when you try to make an action but no community was selected."
        string = "HCL_NO_COMMUNITY_SELECTED"
        self.printException(exception, message, string)

    def communityNotFound(self):
        exception = "CommunityNotFound"
        message = "Triggered when you search for a community but nothing is found."
        string = "HCL_COMMUNITY_NOT_FOUND"
        self.printException(exception, message, string)

    def noChatThread(self):
        exception = "NoChatThread"
        message = "Triggered when you try to make an action but no chat was selected."
        string = "HCL_NO_CHAT_THREAD"
        self.printException(exception, message, string)

    def chatRequestsBlocked(self):
        exception = "ChatRequestsBlocked"
        message = "Triggered when you try to make an action but the end user has chat requests blocked."
        string = "HCL_NO_CHAT_THREAD"
        self.printException(exception, message, string)

    def noImageSource(self):
        exception = "NoImageSource"
        message = "Triggered when you try to make an action but no image source was selected."
        string = "HCL_NO_IMAGE_SOURCE"
        self.printException(exception, message, string)

    def cannotFetchImage(self):
        exception = "CannotFetchImage"
        message = "Triggered when an image cannot be fetched."
        string = "HCL_CANNOT_FETCH_IMAGE"
        self.printException(exception, message, string)

    def failedLogin(self):
        exception = "FailedLogin"
        message = "Triggered when you try to login but it fails."
        string = "HCL_FAILED_LOGIN"
        self.printException(exception, message, string)

    def ageTooLow(self):
        exception = "AgeTooLow"
        message = "Triggered when you try to configure an account but the age is too low. Minimum is 13."
        string = "HCL_USER_AGE_TOO_LOW"
        self.printException(exception, message, string)

    def unsupportedLanguage(self):
        exception = "UnsupportedLanguage"
        message = "Triggered when you try to use a language that isn't supported or exists."
        string = "HCL_UNSUPPORTED_LANGUAGE_BY_AMINO"
        self.printException(exception, message, string)

    def communityNeeded(self):
        exception = "CommunityNeeded"
        message = "Triggered when you try to execute an command but a Community needs to be specified."
        string = "HCL_COMMUNITY_NEEDED"
        self.printException(exception, message, string)

    def flagTypeNeeded(self):
        exception = "FlagTypeNeeded"
        message = "Triggered when you try to flag a community, blog or user but a Flag Type needs to be specified."
        string = "HCL_MISSING_FLAG_TYPE"
        self.printException(exception, message, string)

    def reasonNeeded(self):
        exception = "ReasonNeeded"
        message = "Triggered when you try to execute an command but a Reason needs to be specified."
        string = "HCL_MISSING_REASON"
        self.printException(exception, message, string)

    def failedWebLogin(self):
        exception = "FailedWebLogin"
        message = "Triggered when the api fails to web login"
        string = "HCL_FAILED_WEB_LOGIN"
        self.printException(exception, message, string)

    def transferRequestNeeded(self):
        exception = "TransferRequestNeeded"
        message = "Triggered when you need to transfer host to complete the action."
        string = "HCL_TRANSFER_REQUEST_NEEDED"
        self.printException(exception, message, string)

    def unknownException(self):
        exception = "UnknownException"
        message = "Triggered when the library encountered an unknown exception."
        string = "HCL_UNKNOWN_EXCEPTION"
        self.printException(exception, message, string)


