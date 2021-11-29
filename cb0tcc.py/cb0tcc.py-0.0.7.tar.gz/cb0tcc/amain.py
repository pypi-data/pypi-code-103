from aiohttp import ClientSession

class aiocb0t:
    async def create(self, url):
        async with ClientSession() as session:
            async with session.post("https://cb0t.cc/api/create", data = {"url": url}) as r:
                self.data = await r.json()

    @property
    def url(self):
        return self.data["url"]
