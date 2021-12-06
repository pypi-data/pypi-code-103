import urllib.request
import json


class InviteTools:
    def __init__(self, invite_code):
        self.invite_code = invite_code
        self.invite_info = self.invite_info()
        self.name = self.name()
        self.description = self.description()
        self.id = self.id()
        self.vanity_code = self.vanity_code()
        self.member_count = self.member_count()
        self.online_count = self.online_count()

    def invite_info(self):
        request = urllib.request.Request(
            "https://discord.com/api/v9/invites/{}?with_counts=true".format(self.invite_code)
        )
        request.add_header(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
        )
        response = urllib.request.urlopen(request)
        data = response.read().decode("utf-8")
        data = json.loads(data)
        return (
            data
        )

    def member_count(self):
        return (
            self.invite_info["approximate_member_count"]
        )

    def online_count(self):
        return (
            self.invite_info["approximate_presence_count"]
        )

    def name(self):
        return (
            self.invite_info["guild"]["name"]
        )

    def description(self):
        return (
            self.invite_info["guild"]["description"]
        )

    def id(self):
        return (
            self.invite_info["guild"]["id"]
        )

    def vanity_code(self):
        return (
            self.invite_info["guild"]["vanity_url_code"]
        )

    def icon(self, imagetype: str, size: int):
        if imagetype not in ["png", "jpg", "gif", "webp", "jpeg"]:
            imagetype = "png"
        if size == 16:
            size = "?size=16"
        elif size == 32:
            size = "?size=32"
        elif size == 64:
            size = "?size=64"
        elif size == 128:
            size = "?size=128"
        elif size == 256:
            size = "?size=256"
        elif size == 512:
            size = "?size=512"
        elif size == 1024:
            size = "?size=1024"
        else:
            size = ""
        # if the url returns status code 200, return the url, otherwise return None
        try:
            request = urllib.request.Request(
                f"https://cdn.discordapp.com/banners/{self.invite_info['guild']['id']}/{self.invite_info['guild']['icon']}{size}.{imagetype}"
            )
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
            )
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                return (
                    f"https://cdn.discordapp.com/banners/{self.invite_info['guild']['id']}/{self.invite_info['guild']['icon']}{size}.{imagetype}"
                )
            else:
                return None
        except urllib.error.HTTPError:
            return None

    def banner(self, imagetype: str, size: int):
        if imagetype not in ["png", "jpg", "gif", "webp", "jpeg"]:
            imagetype = "png"
        if size == 16:
            size = "?size=16"
        elif size == 32:
            size = "?size=32"
        elif size == 64:
            size = "?size=64"
        elif size == 128:
            size = "?size=128"
        elif size == 256:
            size = "?size=256"
        elif size == 512:
            size = "?size=512"
        elif size == 1024:
            size = "?size=1024"
        else:
            size = ""
        # if the url returns status code 200, return the url, otherwise return None
        try:
            request = urllib.request.Request(
                f"https://cdn.discordapp.com/banners/{self.invite_info['guild']['id']}/{self.invite_info['guild']['banner']}.{imagetype}{size}"
            )
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
            )
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                return (
                    f"https://cdn.discordapp.com/banners/{self.invite_info['guild']['id']}/{self.invite_info['guild']['banner']}.{imagetype}{size}"
                )
            else:
                return None
        except urllib.error.HTTPError:
            return None

    def splash(self, imagetype: str, size: int):
        if imagetype not in ["png", "jpg", "gif", "webp", "jpeg"]:
            imagetype = "png"
        if size == 16:
            size = "?size=16"
        elif size == 32:
            size = "?size=32"
        elif size == 64:
            size = "?size=64"
        elif size == 128:
            size = "?size=128"
        elif size == 256:
            size = "?size=256"
        elif size == 512:
            size = "?size=512"
        elif size == 1024:
            size = "?size=1024"
        else:
            size = ""
        # if the url returns status code 200, return the url, otherwise return None
        try:
            request = urllib.request.Request(
                f"https://cdn.discordapp.com/splashes/{self.invite_info['guild']['id']}/{self.invite_info['guild']['splash']}.{imagetype}{size}"
            )
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
            )
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                return (
                    f"https://cdn.discordapp.com/splashes/{self.invite_info['guild']['id']}/{self.invite_info['guild']['splash']}.{imagetype}{size}"
                )
            else:
                return None
        except urllib.error.HTTPError:
            return None