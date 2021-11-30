# AIOHTTP SETUP - blog.jonlu.ca

#Time
from time import perf_counter

#Cookies
import http.cookies
http.cookies._is_legal_key=lambda _:True

#Json
from json import loads

#Asyncio
import asyncio
from asyncio import Semaphore, gather

#aiohttp
from aiohttp import TCPConnector, ClientSession

class AsyncAPISpider:
    def __init__(self,par:int=1):
        self.session=ClientSession(connector=TCPConnector(limit=None,ttl_dns_cache=300))
        self.parallel_request_amount=par
        self.loop = asyncio.get_event_loop()
        self.res={}
    
    async def _concurrent_gather(self,n,*tasks):
        sem=Semaphore(n)
        async def sem_t(task):
            async with sem:
                return await task
        x=await gather(*(sem_t(t) for t in tasks))
        await self.session.close()
        return x

    async def _request_async(self,url):
        async with self.session.get(url,ssl=False) as r:
            self.res[url]=loads(await r.read())
            return loads(await r.read())
    
class AAS_URLInterface(AsyncAPISpider):
    def __init__(self,max_requests:int):
        self.s=max_requests
        super().__init__(max_requests)

    def refresh(self):
        self.res={}

    async def request(self,url):
        return self._request_async(url)
        
    async def map(self,urls):
        await self._concurrent_gather(self.s,*urls)
        return [self.res[url] for url in self.res]

    def _req(self,_return:bool=True):
        self.loop.run_until_complete(self._async_req())

