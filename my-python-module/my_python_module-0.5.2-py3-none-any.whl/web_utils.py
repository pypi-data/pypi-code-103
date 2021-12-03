#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import logging
import os
from enum import Enum
from collections import defaultdict
from urllib.parse import urlsplit, urljoin, urldefrag
from datetime import datetime
import threading

import requests
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup, SoupStrainer
from my_fake_useragent import UserAgent
from my_python_module.cache_utils import cachedb, func_cache
from my_python_module.datetime_utils import get_timestamp, get_dt_fromtimestamp
from my_python_module.pathlib import mkdirs

logger = logging.getLogger(__name__)

ua = UserAgent(family=['chrome', 'firefox'])


class URLType(Enum):
    """
    refUrl: 除了Absolute URL，其他URL都需要根据本URL所在的文章的refUrl才能得到绝对URL
    """
    Absolute = 1
    # 'https://www.cis.rit.edu/htbooks/nmr/chap-10/chap-10.htm'
    MissScheme = 2
    # ’//www.cis.rit.edu/htbooks/nmr/chap-10/chap-10.htm‘ refUrl
    RelativeSite = 3
    # ’/htbooks/nmr/chap-10/chap-10.htm‘ refUrl
    RelativeFolder = 4
    # ’chap-10.html‘ refUrl
    RelativeArticle = 5
    # ’#sec1‘
    InValid = 6


def to_absolute_url(url, refUrl):
    """
    给定好refUrl，利用urljoin就能得到绝对url
    refUrl: 除了绝对URL，其他URL都需要根据本URL所在的文章的Url也就是refUrl
            才能得到绝对URL

    如果是爬虫，一开始就将遇到的URL转成绝对URL可能是一个好的选择，但其他文档处理情况则
    不能这样简单处理，需要小心地根据URL的各种类型来采取不同的处理策略。
    """
    return urljoin(refUrl, url)


def is_url_inSite(url, refUrl):
    """
    is the url in site.
    the judgement is based on the refUrl's netloc.

>>> is_url_inSite('https://code.visualstudio.com/docs', \
    'https://code.visualstudio.com/docs/python/linting')
True
    """
    p = urlsplit(url)
    if p.netloc == urlsplit(refUrl).netloc:
        return True
    else:
        return False


def is_url_inArticle(url, refUrl):
    """

    """
    p = urlsplit(url)
    if p.fragment:
        return True
    else:
        return False


def check_url_type(url):
    """
    这里只是对URL类型进行判断，从网络下或的HTML文件需要分辨各种URL类型并采取相应的策略
    """
    p = urlsplit(url)
    if p.scheme and p.netloc and p.path:
        return URLType.Absolute

    if not p.scheme and p.netloc and p.path:
        return URLType.MissScheme

    if not p.scheme and not p.netloc and p.path:
        if p.path.startswith('/'):
            return URLType.RelativeSite
        else:
            return URLType.RelativeFolder
    if not p.scheme and not p.netloc and not p.path:
        if p.fragment:
            return URLType.RelativeArticle
        else:
            return URLType.InValid


def get_url_fragment(url):
    """
    please notice the fragment not include the symbol #
    """
    p = urlsplit(url)
    return p.fragment


def remove_url_fragment(url):
    """
    remove url fragment like `#sec1` and the parameters on url will
    keeped still.
    """
    defragmented, frag = urldefrag(url)
    return defragmented


REPATTEN_URL = re.compile(
    r'https?:\/\/[\da-z\.-]+\.[a-z\.]{2,6}[\/\w\.-]*[\?\w=&#]*')


def parse_urls(text):
    """
    input a text , and return all url we found that based on the re-expression
    of `REPATTEN_URL` . which is not recommend , recommed use the `wget_links` function.
    """
    return re.findall(REPATTEN_URL, text)


def get_webpage_links(html, name='a', id="", class_="", **kwargs):
    """
    :param html: 目标网页的text内容

    input html content, and use the beautifulsoup parse it, get all the
    <a href="link"> and return the link.

    sometime you may want the specific  <a href="link"> which is in where id
    or where class etc.

    you can set `name="div" id="what"'` to narrow the url target into
    the SoupStrainer for the first filter,
    so you can specific which url you want to collect.

    this function will return:
    (
        soup,
        {
            ‘href’: [beatifulsoup4 Tag object, ...]
        }
    )
    """
    all_links = defaultdict(list)
    parse_kwargs = {'name': name}
    if id:
        parse_kwargs['id'] = id
    if class_:
        parse_kwargs['class_'] = class_

    if html:
        soup = BeautifulSoup(
            html, 'html5lib', parse_only=SoupStrainer(**parse_kwargs))
    else:
        logger.error('missing content!')
        return None

    for link in soup.find_all('a', href=True):
        href = link.get('href')

        all_links[href].append(link)

    return soup, all_links


def get_webpage_images(html, name="img", id="", class_="", **kwargs):
    """
    :param html: 目标网页的text内容

    input a html content , and use the beautifulsoup parse it, get all the
    <img src="link"> and return the link.

    sometime you may want the specific  <img src="link"> which is in where id
    or where class etc.

    you can set `name="div" id="what"'` to narrow the url target
    into the SoupStrainer for the first filter,
    so you can specific which url you want to collect.

    this function will return:
    (
        soup,
        {
            ‘src’: [beatifulsoup4 Tag object, ...]
        }
    )
    """
    all_links = defaultdict(list)
    parse_kwargs = {'name': name}
    if id:
        parse_kwargs['id'] = id
    if class_:
        parse_kwargs['class_'] = class_

    if html:
        soup = BeautifulSoup(
            html, 'html5lib', parse_only=SoupStrainer(**parse_kwargs))
    else:
        logger.error('missing content!')
        return None

    for link in soup.find_all('img', src=True):
        src = link.get('src')

        all_links[src].append(link)

    return soup, all_links


def download(url, filename, download_timeout=30, override=False, **kwargs):
    """
    High level function, which downloads URL into tmp file in current
    directory and then renames it to filename autodetected from either URL
    or HTTP headers.
    :param out: output filename or directory
    :return:    filename where URL is downloaded to
    """
    logger.info(f'start downloading file {url} to {filename}')
    import time  # https://github.com/kennethreitz/requests/issues/1803
    start = time.time()

    # make sure folder exists
    mkdirs(os.path.dirname(filename))

    if os.path.exists(filename):
        if override:
            logger.info(f'{filename} exist. but i will override it.')
        else:
            logger.info(f'{filename} exist.')
            return

    content = requests.get(url, stream=True, **kwargs)

    with open(filename, 'wb') as f:
        for chunk in content.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
            if time.time() - start > download_timeout:
                content.close()
                os.unlink(filename)
                logger.warning('{0} download failed'.format(filename))
                return False

    return filename


def use_cache_callback_requests_web(cache_data, func, args, kwargs,
                                    use_cache_oldest_dt=None):
    timestamp = cache_data.get('timestamp', get_timestamp())
    data_dt = get_dt_fromtimestamp(timestamp)

    if use_cache_oldest_dt is None:
        target_dt = datetime.now() - relativedelta(
            seconds=14)  # default 14 days
    else:
        target_dt = use_cache_oldest_dt

    if data_dt < target_dt:  # too old then we will re-excute the function
        t = threading.Thread(target=_update_requests_web,
                             args=(cache_data, args))
        t.daemon = True
        t.start()


def _update_requests_web(cache_data, args):
    logger.info('update_requests_web')
    headers = {
        'user-agent': ua.random()
    }
    url = args[0]
    data = requests.get(url, headers=headers, timeout=30)

    cache_data['data'] = data
    cache_data['timestamp'] = str(get_timestamp())
    key = cache_data.get('key')

    cachedb.set(key, cache_data)
    return data


@func_cache(use_cache_callback=use_cache_callback_requests_web)
def requests_web(url):
    """
    有数据则直接使用 没有数据则试着从网络上请求
    直接使用数据的时候会根据数据的时间戳来判断新旧，如果数据过旧则启动后台更新线程

    :param url:
    :return:
    """
    headers = {
        'user-agent': ua.random()
    }

    data = requests.get(url, headers=headers, timeout=30)

    return data


def is_url_belong(url, baseurl):
    """
    is the url belong to the baseurl.
    the check logic is strict string match.
    """
    if url.startswith(baseurl):
        return True
    else:
        return False
