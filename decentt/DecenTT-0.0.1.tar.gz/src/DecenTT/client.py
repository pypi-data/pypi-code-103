from DecenTT.DecenTTErrors import InvalidCallback
from DecenTT.IPFS import Client as iClient
from DecenTT.MQTT import Client as mClient


class Client:
    """
        Which Client ??
        0:          MQTT Client
        1:          IPFS Client

    """

    def __init__(
            self,
            host: str,
            port: int = 1883,
            username: str = None,
            password: str = None,
            on_connect=None,
            on_publish=None,
            on_message=None,
            log_path: str = ".",
            keyword: str = "secure/"
    ) -> None:
        self.__keyword = keyword
        self.clients = [
            mClient(
                host=host,
                port=port,
                username=username,
                password=password,
                on_connect=on_connect,
                on_publish=on_publish,
                on_message=on_message,
                log_path=log_path
            ),

            iClient()
        ]

    # Mock Switcher
    def __which(self, topic: str):
        if self.__keyword in topic: return self.clients[1]
        return self.clients[0]

    def subscribe(self, topic: str, callback):
        # check for valid callback
        if not ('function' in str(type(callback))):
            raise InvalidCallback(callback)
        client = self.__which(topic=topic)
        client.subscribe(topic=topic, callback=callback)

    def publish(self, topic: str, payload: str):
        client = self.__which(topic=topic)
        client.publish(topic=topic, payload=payload)
