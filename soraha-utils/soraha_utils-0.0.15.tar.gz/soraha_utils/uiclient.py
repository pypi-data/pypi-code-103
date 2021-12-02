import requests
import httpx
from typing import AnyStr, Optional, Union

from .uilog import logger
from .uitry import retry


class sync_uiclient:
    def __init__(
        self,
        proxy: Optional[dict] = None,
        timeout: Optional[Union[tuple, int]] = None,
        request_headers: Optional[dict] = None,
        other_headers: Optional[dict] = None,
        request_json: Optional[AnyStr] = None,
        request_params: Optional[dict] = None,
        request_data: Optional[dict] = None,
    ) -> None:
        """同步下的网络连接请求,如果需要保存图片/json响应请使用uio下的save_file,提供了相同的网络请求功能。
        使用示例:
        ```
        with sync_uiclient() as cl:
            res = cl.uiget(url)

        print(res.status_code)
        >>> 200
        ```

        Args:
            proxy (Optional[dict], optional): 代理. Defaults to None.
            timeout (Optional[Union[tuple, int]], optional): 超时设置. Defaults to None.
            request_headers (Optional[dict], optional): headers,默认有国内windows电脑的头部请求,没有特殊需要可以不用管. Defaults to None.
            other_headers (Optional[dict], optional): 额外headers,传入字典,会替换/加入headers里. Defaults to None.
            request_json (Optional[AnyStr], optional): 需要提交的json. Defaults to None.
            request_params (Optional[dict], optional): 需要提交的param. Defaults to None.
            request_data (Optional[dict], optional): 需要提交的data. Defaults to None.
        """
        self.headers = {
            "sec-ch-ua": """Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99""",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        }
        if request_headers:
            self.headers = request_headers
        if other_headers:
            for x, y in other_headers.items():
                self.headers[x] = y
        self.proxy = proxy
        self.timeout = timeout
        self.params = request_params
        self.data = request_data
        self.json = request_json

    def __enter__(self) -> None:
        return self

    def __exit__(self, excep_type, excep_value, traceback) -> None:
        pass

    @retry(logger=logger)
    def uiget(self, url: str) -> requests.get:
        """get的请求函数,使用的是requests

        Args:
            url (str): 需要请求的url

        Returns:
            requests.get(): 返回请求成功后的连接
        """
        logger.debug(
            f"开始连接至:{url},方法:GET,代理:{self.proxy},参数:{self.params},数据:{self.data}"
        )
        res = requests.get(
            url,
            proxies=self.proxy,
            timeout=self.timeout,
            json=self.json,
            headers=self.headers,
            params=self.params,
            data=self.data,
        )
        logger.debug(f"成功连接,状态码:{res.status_code}")
        return res

    @retry(logger=logger)
    def uipost(self, url: str):
        """post的请求函数,使用的是requests

        Args:
            url (str): 需要请求的url

        Returns:
            requests.get(): 返回请求成功后的连接
        """
        logger.debug(
            f"开始连接至:{url},方法:POST,代理:{self.proxy},参数:{self.params},数据:{self.data}"
        )
        res = requests.post(
            url,
            proxies=self.proxy,
            timeout=self.timeout,
            headers=self.headers,
            json=self.json,
            params=self.params,
            data=self.data,
        )
        logger.debug(f"成功连接,状态码:{res.status_code}")
        return res


class async_uiclient:
    def __init__(
        self,
        proxy: Optional[dict] = None,
        timeout: Optional[Union[tuple, int]] = None,
        request_headers: Optional[dict] = None,
        other_headers: Optional[dict] = None,
        request_json: Optional[AnyStr] = None,
        request_params: Optional[dict] = None,
        request_data: Optional[dict] = None,
    ) -> None:
        """异步下的网络连接请求,如果需要保存图片/json响应请使用uio下的save_file,提供了相同的网络请求功能。
        使用示例:
        ```
        async with sync_uiclient() as cl:
            res = await cl.uiget(url)

        print(res.status_code)
        >>> 200
        ```

        Args:
            proxy (Optional[dict], optional): 代理. Defaults to None.
            timeout (Optional[Union[tuple, int]], optional): 超时设置. Defaults to None.
            request_headers (Optional[dict], optional): headers,默认有国内windows电脑的头部请求,没有特殊需要可以不用管. Defaults to None.
            other_headers (Optional[dict], optional): 额外headers,传入字典,会替换/加入headers里. Defaults to None.
            request_json (Optional[AnyStr], optional): 需要提交的json. Defaults to None.
            request_params (Optional[dict], optional): 需要提交的param. Defaults to None.
            request_data (Optional[dict], optional): 需要提交的data. Defaults to None.
        """
        self.headers = {
            "sec-ch-ua": """Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99""",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        }
        if request_headers:
            self.headers = request_headers
        if other_headers:
            for x, y in other_headers.items():
                self.headers[x] = y
        self.proxy = proxy
        self.timeout = timeout
        self.json = request_json
        self.params = request_params
        self.data = request_data

    async def __aenter__(self) -> None:
        return self

    async def __aexit__(self, excep_type, excep_value, traceback) -> None:
        pass

    @retry(logger=logger)
    async def uiget(self, url: str) -> httpx.AsyncClient.get:
        """get的请求函数,使用的是httpx

        Args:
            url (str): 需要请求的url

        Returns:
            httpx.AsyncClient.get: 返回请求成功后的连接
        """
        logger.debug(
            f"开始连接至:{url},方法:GET,代理:{self.proxy},参数:{self.params},数据:{self.data}"
        )
        async with httpx.AsyncClient(
            proxies=self.proxy,
            timeout=self.timeout,
            headers=self.headers,
            params=self.params,
        ) as client:
            res = await client.get(
                url,
            )
        logger.debug(f"成功连接,状态码:{res.status_code}")
        return res

    @retry(logger=logger)
    async def uipost(self, url: str) -> httpx.AsyncClient.post:
        """post的请求函数,使用的是httpx

        Args:
            url (str): 需要请求的url

        Returns:
            httpx.AsyncClient.post: 返回请求成功后的连接
        """
        logger.debug(
            f"开始连接至:{url},方法:POST,代理:{self.proxy},参数:{self.params},数据:{self.data}"
        )
        async with httpx.AsyncClient(
            proxies=self.proxy,
            timeout=self.timeout,
            headers=self.headers,
            params=self.params,
        ) as client:
            res = await client.post(url, data=self.data, json=self.json)
        logger.debug(f"成功连接,状态码:{res.status_code}")
        return res
