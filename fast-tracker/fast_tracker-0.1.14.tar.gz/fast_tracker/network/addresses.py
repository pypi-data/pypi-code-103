# -*- coding: utf-8 -*-

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def proxy_details(proxy_scheme, proxy_host, proxy_port, proxy_user, proxy_pass):

    if not proxy_host:
        return

    components = urlparse.urlparse(proxy_host)

    if not components.scheme and not proxy_port:
        return

    path = ''

    if components.scheme:
        proxy_scheme = components.scheme
        netloc = components.netloc
        path = components.path

    elif components.path:
        netloc = components.path

    else:
        netloc = proxy_host

    if proxy_port:
        netloc = '%s:%s' % (netloc, proxy_port)

    if proxy_user:
        proxy_user = proxy_user or ''
        proxy_pass = proxy_pass or ''

        if proxy_pass:
            netloc = '%s:%s@%s' % (proxy_user, proxy_pass, netloc)
        else:
            netloc = '%s@%s' % (proxy_user, netloc)
    if proxy_scheme is None:
        proxy_scheme = 'http'

    proxy = '%s://%s%s' % (proxy_scheme, netloc, path)

    return {'http': proxy, 'https': proxy}
