import requests
from requests.exceptions import HTTPError

from anylearn.config import AnylearnConfig

url_base = lambda :AnylearnConfig.cluster_address + '/api'


def __intercept(**kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Authorization'] = "Bearer %s" % AnylearnConfig.token
    return kwargs


def __raise_for_status(res: requests.Response):
    http_error_msg = ''
    if isinstance(res.reason, bytes):
        try:
            reason = res.reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = res.reason.decode('iso-8859-1')
    else:
        reason = res.reason
    
    if isinstance(res.content, bytes):
        try:
            content = res.content.decode('utf-8')
        except UnicodeDecodeError:
            content = res.content.decode('iso-8859-1')
    else:
        content = res.content

    if 400 <= res.status_code < 500:
        http_error_msg = u'%s: "%s" for url: %s' % (res.status_code, content, res.url)

    elif 500 <= res.status_code < 600:
        http_error_msg = u'%s: "%s" for url: %s' % (res.status_code, reason, res.url)

    if http_error_msg:
        raise HTTPError(http_error_msg, response=res)


def get_with_token(*args, **kwargs):
    kwargs = __intercept(**kwargs)
    with requests.session() as sess:
        res = sess.get(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()


def post_with_token(*args, **kwargs):
    kwargs = __intercept(**kwargs)
    with requests.session() as sess:
        res = sess.post(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()


def post_with_secret_key(*args, secret_key, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['secret_key'] = secret_key
    with requests.session() as sess:
        res = sess.post(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()


def delete_with_token(*args, **kwargs):
    kwargs = __intercept(**kwargs)
    with requests.session() as sess:
        res = sess.delete(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()


def put_with_token(*args, **kwargs):
    kwargs = __intercept(**kwargs)
    with requests.session() as sess:
        res = sess.put(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()


def patch_with_token(*args, **kwargs):
    kwargs = __intercept(**kwargs)
    with requests.session() as sess:
        res = sess.patch(*args, **kwargs)
        __raise_for_status(res)
        res.encoding = "utf-8"
        return res.json()
