from google import auth
from telegram.ext import MessageFilter
import requests as req
from requests.exceptions import Timeout
from configparser import ConfigParser 
import os
  
config = ConfigParser() 
config.read('config.ini')

class FilterRasa(MessageFilter):
    def __init__(self, intent, confidence=0.8):
        self.intent = intent
        self.confidence = confidence
        
    def filter(self, message):
        try:
            RASA_TOKEN = os.getenv('RASA_TOKEN')
            response = req.post(config["rasa"]["url"] + "/api/projects/default/logs", params={"q": message.text}, headers={'Authorization': 'Bearer {}'.format(RASA_TOKEN)},  timeout = (3, 8))
            print(response.json())
        except Timeout:
            False
        else:
            if not response.ok:
                return False                                                         
            return response.json()["user_input"]["intent"]["name"] == self.intent and response.json()["user_input"]["intent"]["confidence"] >= self.confidence