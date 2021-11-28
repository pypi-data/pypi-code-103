import os

from typing import Union, NamedTuple, List, Any
from requests import Response, Session
from Crypto.Hash import SHA256
from uuid import uuid4
from json import loads

from .errors import ApplicationDoesntExist
from .encryption import encrypt_hex, encrypt, decrypt
from .types import InitializeResult, KeyAuthResult, RegisterResult, Subscription
from .utils import get_hwid

class Message(NamedTuple):
    """Message object."""

    author: str
    message: str
    timestamp: str

class KeyAuth:
    def __init__(self, name: str, owner_id: str, secret: str, version: str, app_hash: str = None, auto_initialize: bool = True, test_mode: bool = False) -> None:
        self.name = name
        self.secret = secret
        self.version = version
        self.app_hash = app_hash
        self.owner_id = owner_id

        self.__session_iv = str(uuid4())[:8]
        self.__session_id = ""
        self.__session = Session()

        self.__enckey = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        self.__is_initialized = False

        if auto_initialize:
            self.initialize(test_mode)

    @property
    def is_initialized(self) -> bool:
        return self.__is_initialized
        
    def initialize(self, test_mode: bool) -> InitializeResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("init".encode()),
            "name": encrypt_hex(self.name.encode()),
            "ver": encrypt(self.version, self.secret, init_iv),
            "init_iv": init_iv,
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "enckey": encrypt(self.__enckey, self.secret, init_iv)
        }

        if test_mode and len(self.app_hash) > 1:
            post_data["hash"] = self.app_hash

        response = self._request(post_data)
        if "KeyAuth_Invalid" in response.text:
            raise ApplicationDoesntExist("The application doesn't exist in keyauth.")

        results = loads(decrypt(response.text, self.secret, init_iv))
        if not results["success"]:
            return InitializeResult(message=results["message"])

        self.__is_initialized = True
        self.__session_id = results["sessionid"]

        return InitializeResult(is_success=True)

    def login(self, username: str, password: str, user_hwid: str = None) -> KeyAuthResult:
        if user_hwid is None:
            user_hwid = get_hwid()

        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("login".encode()),
            "username": encrypt(username, self.__enckey, init_iv),
            "pass": encrypt(password, self.__enckey, init_iv),
            "hwid": encrypt(user_hwid, self.__enckey, init_iv),
			"sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message="Successfully logged in.")

    def register(self, username: str, password: str, license_key: str, user_hwid: str = None) -> RegisterResult:
        if user_hwid is None:
            user_hwid = get_hwid()

        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("register".encode()),
            "username": encrypt(username, self.__enckey, init_iv),
            "pass": encrypt(password, self.__enckey, init_iv),
            "key": encrypt(license_key, self.__enckey, init_iv),
            "hwid": encrypt(user_hwid, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return RegisterResult(message=results["message"])

        return self._get_register_object(results)

    def upgrade(self, username: str, license_key: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("upgrade".encode()),
            "username": encrypt(username, self.__enckey, init_iv),
            "key": encrypt(license_key, self.__enckey, init_iv),
			"sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message="Successfully upgraded user.")

    def send_chat(self, message: str, channel_name: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("chatsend".encode()),
            "message": encrypt(message, self.__enckey, init_iv),
            "channel": encrypt(channel_name, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message="Sent message successfully.")

    def get_chat(self, channel_name: str) -> List[Message]:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("chatget".encode()),
            "channel": encrypt(channel_name, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(
            is_success=True,
            message=[Message(author=msg["author"], message=msg["message"], timestamp=msg["timestamp"])
                    for msg in results["messages"]]
        )

    def blacklist(self, channel_name: str) -> List[Message]:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("chatget".encode()),
            "channel": encrypt(channel_name, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(
            is_success=True,
            message=[Message(author=msg["author"], message=msg["message"], timestamp=msg["timestamp"])
                    for msg in results["messages"]]
        )

    def license_key(self, key: str, user_hwid: str = None) -> KeyAuthResult:
        if user_hwid is None:
            user_hwid = get_hwid()

        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("license".encode()),
            "key": encrypt(key, self.__enckey, init_iv),
            "hwid": encrypt(user_hwid, self.__enckey, init_iv),
			"sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message="Successfully logged with license key.")

    def get_variable(self, name: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("getvar".encode()),
            "var": encrypt(name, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message=results["response"])

    def save_variable(self, name: str, data: Any) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("setvar".encode()),
            "var": encrypt(name, self.__enckey, init_iv),
            "data": encrypt(data, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message=results["message"])

    def variable(self, name: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("var".encode()),
            "varid": encrypt(name, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message=results["message"])

    def get_file(self, file_id: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("file".encode()),
            "fileid": encrypt(file_id, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message=results["contents"])

    def webhook(self, webhook_id: str, params: str) -> KeyAuthResult:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("webhook".encode()),
            "webid": encrypt(webhook_id, self.__enckey, init_iv),
            "params": encrypt(params, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }
        
        response = self._request(post_data)
        results = loads(decrypt(response.text, self.__enckey, init_iv))

        if not results["success"]:
            return KeyAuthResult(message=results["message"])

        return KeyAuthResult(is_success=True, message=results["message"])

    def log(self, message: str) -> None:
        init_iv = SHA256.new(str(uuid4())[:8].encode()).hexdigest()
        post_data = {
            "type": encrypt_hex("log".encode()),
            "pcuser": encrypt(os.getenv('username'), self.__enckey, init_iv),
            "message": encrypt(message, self.__enckey, init_iv),
            "sessionid": encrypt_hex(self.__session_id.encode()),
            "name": encrypt_hex(self.name.encode()),
            "ownerid": encrypt_hex(self.owner_id.encode()),
            "init_iv": init_iv
        }

        self._request(post_data)

    def _request(self, post_data: Union[str, dict], **kwargs) -> Response:
        return self.__session.post(
            url="https://keyauth.win/api/1.0/",
            data=post_data,
            **kwargs
        )

    def get_keysave_path(self) -> str:
        """You can save the user key/credentials."""
        return "C:\\ProgramData\\keysave.txt" if os.name == "nt" else "/usr/keysave.txt"

    def _get_register_object(self, results: dict) -> RegisterResult:
        return RegisterResult(
            subscriptions=[Subscription(level=sub["subscription"], expiry=sub["expiry"]) for sub in results["info"]["subscriptions"]],
            register_ip=results["info"]["ip"],
            is_success=True,
            message="Successfully registered."
        )