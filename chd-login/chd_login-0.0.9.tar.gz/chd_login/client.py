import bs4
import requests

from chd_login.encrypt import encrypt


class IDSClient(object):
    """
    Login Client
    """

    def __init__(self, login_url, proxies=None, need_detail=False, need_session=False):
        """
        :param proxies: proxy settings dict
        e.g. proxies = {
            "http": "http://proxy:123456@127.0.0.1:888",
            "https": "http://proxy:123456@127.0.0.1:888"
        }
        :param need_detail: detail when login success
        """
        self.web = requests.session()
        self.web.proxies = proxies
        self.web.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/59.0.3071.115 Safari/537.36"
        }
        self.login_data = {
            "username": "",
            "password": "",
            "captcha": "",
            "_eventId": "submit",
            "cllt": "userNameLogin",
            "lt": "",
            "execution": "",
        }
        self.login_url = login_url
        self.need_detail = need_detail
        self.need_session = need_session

    def _verify(self, uid, password):
        """
        make sure you are using string when login
        """
        assert uid, "工号/学号不能为空."
        assert password, "密码不能为空."
        assert isinstance(uid, str), "学号应为字符串类型."
        assert isinstance(password, str), "密码应为字符串类型."

    def login(self, uid: str, password: str):
        """
        :param uid: student id or teacher id
        :param password:  password
        :return: Result Code, Detail, requests.session()
        Result Code 200 - Login Success
        Result Code 401 - Wrong Username or Password
        Result Code 500 - Unknown Error
        """
        self._verify(uid, password)
        try:
            html = self.web.get(self.login_url)
            soup = bs4.BeautifulSoup(html.text, "html.parser")
            key = soup.find("input", attrs={"id": "pwdEncryptSalt"})["value"]
            self.login_data["username"] = uid
            self.login_data["password"] = encrypt(password, key)
            self.login_data["execution"] = soup.find(
                "input", attrs={"name": "execution"}
            )["value"]
            resp = self.web.post(self.login_url, data=self.login_data)
            if resp.status_code == 401:
                return 401, "工号/学号或密码错误", None
            mod_auth_cas = self.web.cookies.get("MOD_AUTH_CAS", None)
            castgc = self.web.cookies.get("CASTGC", None)
            auth_token = mod_auth_cas or castgc
            if auth_token:
                data = [
                    200,
                ]
                data.append(
                    {
                        "user": uid,
                        "params": {
                            cookie: value for cookie, value in self.web.cookies.items()
                        },
                    }
                ) if self.need_detail else data.append(None)
                data.append(self.web) if self.need_session else data.append(None)
                return data
            raise Exception("IDS Cookie 有误, 请联系管理员.")
        except Exception as err:
            return 500, str(err), None
