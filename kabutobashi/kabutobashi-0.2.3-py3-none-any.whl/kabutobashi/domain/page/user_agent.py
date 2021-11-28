import random
from dataclasses import dataclass


class UserAgent:
    @staticmethod
    def get_user_agent() -> str:
        user_agent_list = [Chrome().user_agent, Firefox().user_agent]
        return random.choice(user_agent_list)

    @staticmethod
    def get_user_agent_header() -> dict:
        return {"User-Agent": UserAgent.get_user_agent()}


@dataclass
class Browser:
    """
    user_agentを生成するクラス
    user_agent_formatとbrowser_versionを受け取り、USER_AGENTを生成する
    """

    user_agent_format: str
    browser_version: str

    def __post_init__(self):
        self.user_agent = self.user_agent_format.format(version=self.browser_version)


class Chrome:
    """
    Google ChromeのUSER_AGENTを生成するクラス
    """

    def __init__(self):
        os_format_list = [
            # mac_chrome_format
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
            # windows_chrome_format
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}",
        ]

        version_list = ["77.0.3865", "78.0.3904", "79.0.3945.130", "80.0.3987", "81.0.4044", "83.0.4103.97"]

        browser = Browser(random.choice(os_format_list), random.choice(version_list))
        self.user_agent = browser.user_agent


class Firefox:
    """
    FirefoxのUSER_AGENTを生成するクラス
    """

    def __init__(self):
        os_format_list = [
            # mac_firefox_format
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/{version}",
            # windows_firefox_format
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/{version}",
        ]

        version_list = ["68.4.2", "72.0.2", "73.0", "74.0"]

        browser = Browser(random.choice(os_format_list), random.choice(version_list))
        self.user_agent = browser.user_agent
