from .config import Config
from .http import Http
from .mqtt import Mqtt
import json

class Service():
    default_config = {
            "ADDR": "127.0.0.1",
            "PORT": "10100",
            "WORKDIR": ".",
            "MQTT_ADDR": "localhost",
            "MQTT_PORT": 1883
        }

    def __init__(self, cfg: object, srv_name: str):
        self.config = Config(self.default_config)
        self.config.from_object(cfg)
        self.srv_name = srv_name
        self.http = Http(self.config, self.srv_name)
        self.http.srv = self
        
        self.mqtt = Mqtt(self.config['MQTT_ADDR'], self.config['MQTT_PORT'])
        self.mqtt.srv = self

    def Bind(self, app):
        self.app = app
        self.http.Build()

    # def parse(self, model_str: str) -> object:

    def ReadProperty(self, key: str):
        print("Read property: " + key)
        return getattr(self.app, key)
        
    def WriteProperty(self, key:str, content:str):
        print("Write property: " + key)
        print(content)
        setattr(self.app, key, json.loads(content))

    def Execute(self, func_name:str, content:str = None):
        print("Execute function: " + func_name)
        if (content == None):
            return getattr(self.app, func_name)()
        else:
            print(content)
            return getattr(self.app, func_name)(**(json.loads(content)))