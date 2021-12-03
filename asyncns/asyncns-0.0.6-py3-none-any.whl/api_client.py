import aiohttp
from utils.ratelimit import Limiter
from xml.etree import ElementTree

limiter = Limiter(limit=50, interval=30)


class ApiClient:
    """
    An API wrapper for the NationStates API.

    TODO: Write documentation
    """

    def __init__(self, useragent: str):
        self.useragent = useragent
        self.password = None
        self.headers = {
            "User-Agent": self.useragent,
        }
        self.session = aiohttp.ClientSession()

    @limiter
    async def dispatch(self, data: dict):
        """
        Makes a post request to the NS API to prepare the dispatch private command.
        Parses the response for the token, then executes the request with the token appended.
        You must set a password with client.password before calling this method.
        :param data:
        :return:
        """
        # Set the password in the headers
        self.headers.update({"X-Password": self.password})
        response = await self.session.post(
            "https://www.nationstates.net/cgi-bin/api.cgi",
            data=data,
            headers=self.headers,
        )
        # The API returns data in the form of an XML document, so we parse it here
        response_data = await response.text()
        # The token is contained in a <SUCCESS> tag
        root = ElementTree.fromstring(response_data)
        token = root.find("SUCCESS").text
        # The dispatch command requires the token to be appended to the URL
        data.update({"token": token})
        # Change from prepare to execute
        data.update({"mode": "execute"})
        # Get the X-Pin header and set it in the headers
        x_pin = response.headers["X-Pin"]
        self.headers.update({"X-Pin": x_pin})
        # Pop the password from the headers
        self.headers.pop("X-Password")
        # Execute the command
        final = await self.session.post(
            "https://www.nationstates.net/cgi-bin/api.cgi",
            data=data,
            headers=self.headers,
        )
        if final.status == 200:
            print("Dispatch posted successfully.")
        else:
            print("Dispatch failed.")
            text = await final.text()
            print(text)

    @limiter
    async def _get(self, url: str, params: dict = None, private: bool = False):
        """
        Perform a GET request to the API.

        :param url: The URL to request
        :param params: The parameters to pass to the request
        :return: The response from the API
        :rtype: str
        """
        if not private:
            text = ""
            async with self.session.get(url, params=params) as response:
                text = await response.text()
            return text
        if private:
            text = ""
            self.headers.update({"X-Password": self.password})
            async with self.session.get(url, params=params, headers=self.headers) as response:
                text = await response.text()
            return text

    @limiter
    async def _post(self, url: str, data: dict = None, private: bool = False):
        """
        Perform a POST request to the API.

        :param url: The URL to request
        :param data: The data to pass to the request
        :return: The response from the API
        :rtype: str
        """

        if not private:
            text = ""
            async with self.session.post(url, data=data, headers=self.headers) as response:
                text = await response.text()
            return text
        if private:
            text = ""
            self.headers.update({"X-Password": self.password})
            async with self.session.post(url, data=data, headers=self.headers) as response:
                text = await response.text()
            return text

    async def get_nation(self, nation: str, shard: str = None):
        """
        Performs a lookup on a nation.

        :param shard: str
        :param nation: str
        :return: XML response from the API
        :rtype: str
        """
        if not shard:
            url = "https://www.nationstates.net/cgi-bin/api.cgi"
            params = {
                "nation": nation,
            }
            return await self._get(url, params=params)
        else:
            url = "https://www.nationstates.net/cgi-bin/api.cgi"
            params = {
                "nation": nation,
                "q": shard,
            }
            return await self._get(url, params=params)

    async def get_region(self, region: str, shard: str = None):
        """
        Performs a lookup on a region.

        :param shard: str
        :param region: str
        :return: XML response from the API
        :rtype: str
        """
        if not shard:
            url = "https://www.nationstates.net/cgi-bin/api.cgi"
            params = {
                "region": region,
            }
            return await self._get(url, params=params)
        else:
            url = "https://www.nationstates.net/cgi-bin/api.cgi"
            params = {
                "region": region,
                "q": shard,
            }
            return await self._get(url, params=params)

    async def world_api(self, shard: str):
        """
        Queries the World API.

        :param shard: str
        :return:
        """
        url = "https://www.nationstates.net/cgi-bin/api.cgi"
        params = {
            "q": shard,
        }
        return await self._get(url, params=params)
