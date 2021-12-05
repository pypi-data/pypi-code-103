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

    def ReadProperty(self, key: str, content):
        print("Read property: " + key)
        try: # Service mode
            return getattr(self.app, key)
        except: # Protocol mode (need implementation)
            return self.app.ReadProperty(key, content) 
        
    def WriteProperty(self, key:str, content):
        print("Write property: " + key)
        print(content)
        try: # Service
            setattr(self.app, key, content)
        except: # Protocol
            return self.app.WriteProperty(key, content)

    def Execute(self, func_name:str, content = None):
        print("Execute function: " + func_name)
        if (content == None):
            return getattr(self.app, func_name)()
        else:
            print(content)
            if isinstance(content, str):
                return getattr(self.app, func_name)(**(json.loads(content)))
            elif isinstance(content, dict):
                return getattr(self.app, func_name)(**content)
            else:
                return "Content type is not supported"