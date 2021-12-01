import requests

class Line:

    __NOTIFY_URL = 'https://notify-api.line.me/api/notify'

    def __init__(self, token:str) -> None:
        self.token = token
        self.headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + token
        }

    def send_msg(self, msg:str):
        r= requests.post(self.__NOTIFY_URL, headers=self.headers, data = {'message':msg})
        return r
