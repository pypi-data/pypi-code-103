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
        self.session=ClientSession(connector=TCPConnector(limit=None,limit_per_host=par,ttl_dns_cache=300))
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

    async def _request_async(self,url,decoding='utf-8',headers={},params={},ssl=False,allow_redirects=True):
        async with self.session.get(url=url,headers=headers,params=params,ssl=ssl,allow_redirects=allow_redirects) as r:
            r=await r.read()
            r=r.decode(decoding)
            print(r)
            self.res[url]=r
            return r
    
class AAS_URLInterface(AsyncAPISpider):
    def __init__(self,request_limit_per_host:int):
        self.s=request_limit_per_host
        super().__init__(request_limit_per_host)

    def refresh(self):
        self.res={}

    async def request(self,url,headers={},params={},ssl=False,allow_redirects=True):
        return self._request_async(url,headers=headers,params=params,ssl=ssl,allow_redirects=allow_redirects)
        
    async def map(self,urls,load=False):
        await self._concurrent_gather(self.s,*urls)
        u=[self.res[url] for url in self.res]
        if load:
            return [loads(url) for url in u]
        return u

