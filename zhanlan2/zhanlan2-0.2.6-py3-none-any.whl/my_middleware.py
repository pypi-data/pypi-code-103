#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/25 16:33
# @Author  : Adyan
# @File    : my_middleware.py


import random
import time
import requests
import logging

# from twisted.internet import defer, reactor
from twisted.internet import defer
from twisted.internet.error import ConnectionRefusedError

from scrapy import signals
from scrapy.http import TextResponse
from scrapy.core.downloader.handlers.http11 import TunnelError, TimeoutError
from gerapy_pyppeteer.downloadermiddlewares import reactor

from .proxy import ProxyGetter


class Proxy(object):

    def __init__(self, settings, spider):
        self.settings = settings
        self.ip_list = []
        self.ip_data = 0
        try:
            proxy = spider.proxy
            self.proxies = ProxyGetter(
                proxy.get('url'),
                proxy.get('name'),
                add_whitelist=proxy.get('add_whitelist'),
                del_whitelist=proxy.get('del_whitelist')
            )
        except:
            pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler.spider)

    def process_response(self, request, response, spider):
        """
        处理响应
        :param request:
        :param response:
        :param spider:
        :return:
        """
        try:
            if spider.proxy:
                start_time = request.meta.get('_start_time', time.time())
                logging.info(
                    f'【代理{request.meta["proxy"][8:]}消耗时间】 {request.url} {time.time() - start_time}'
                )
                del request.meta["proxy"]
        except:
            pass
        return response

    def process_request(self, request, spider):
        """
        处理请求
        :param request:
        :param spider:
        :return:
        """
        request.meta.update(
            {
                '_start_time': time.time()
            }
        )
        try:
            proxy_switch = spider.proxy
        except:
            proxy_switch = False

        if proxy_switch:
            if len(self.ip_list) < 2:
                proxies = self.proxies.get_proxies()
                if not proxies:
                    self.proxies.get_proxies()
                else:
                    self.ip_list = self.proxies.get_proxies()
                    self.ip_data = time.time() + 300

            request.meta['download_timeout'] = 5

            if self.ip_list:
                ip_raw = random.choice(self.ip_list)
                self.ip_list.remove(ip_raw)
                request.meta["proxy"] = ip_raw
            else:
                logging.info('代理列表为空')

    def process_exception(self, request, exception, spider):
        """
        过滤代理错误
        :param request:
        :param exception:
        :param spider:
        :return:
        """
        if isinstance(exception, (TunnelError, TimeoutError, ConnectionRefusedError)):
            return request


class Request(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    @defer.inlineCallbacks
    def process_request(self, request, spider):
        container = []
        out = defer.Deferred()
        reactor.callInThread(self._get_res, request, container, out)
        yield out
        if len(container) > 0:
            defer.returnValue(container[0])

    def _get_res(self, request, container, out):
        url = request.url
        r = requests.get(url, headers=request.meta.get("headers"))
        r.encoding = request.encoding
        text = r.content

        # response = TextResponse(url=r.url, status=r.status_code, body=r.text, request=request)
        response = TextResponse(url=r.url, encoding="gbk", body=text, request=request)
        container.append(response)
        reactor.callFromThread(out.callback, response)
        # except Exception as e:
        #     err = str(type(e)) + ' ' + str(e)
        #     reactor.callFromThread(out.errback, ValueError(err))

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
