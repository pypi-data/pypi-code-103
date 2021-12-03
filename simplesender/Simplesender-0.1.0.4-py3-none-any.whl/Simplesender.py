import requests
import asyncio

class sender:
    def __init__(self, url:str, cont:str, usn:str):
        self.url = url
        self.cont = cont
        self.usn = usn

    async def send(self):
        url = self.url
        content = self.cont
        username = self.usn
        data = {
            "content" : content,
            "username" : username 
        }

        req = requests.post(url, json = data)

        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return print(err)
        else:
            return print("전송완료, 코드 {}".format(req.status_code))

    def sends(self):
        asyncio.run(sender.send(self))

    

        