# -*- coding: utf-8 -*-
import json
import requests
from .exceptions import TelegraphException
from .utils import html_to_nodes, nodes_to_html


class TelegraphApi(object):
    __slots__ = ('access_token', 'session')
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.session = requests.Session()

    def method(self, method, values=None, path=''):
        values = values.copy() if values is not None else {}

        if 'access_token' not in values and self.access_token:
            values['access_token'] = self.access_token

        response = self.session.post(
            'https://api.telegra.ph/{}/{}'.format(method, path),
            values
        ).json()

        if response.get('ok'):
            return response['result']

        raise TelegraphException(response.get('error'))


class Telegraph(object):
    __slots__ = ('_telegraph',)
    def __init__(self, access_token=None):
        self._telegraph = TelegraphApi(access_token)

    def get_access_token(self):
        return self._telegraph.access_token

    def create_account(self, short_name, author_name=None, author_url=None,
                       replace_token=True):
        response = self._telegraph.method('createAccount', values={
            'short_name': short_name,
            'author_name': author_name,
            'author_url': author_url
        })
        if replace_token:
            self._telegraph.access_token = response.get('access_token')
        return response

    def edit_account_info(self, short_name=None, author_name=None,
                          author_url=None):
        return self._telegraph.method('editAccountInfo', values={
            'short_name': short_name,
            'author_name': author_name,
            'author_url': author_url
        })

    def revoke_access_token(self):
        response = self._telegraph.method('revokeAccessToken')

        self._telegraph.access_token = response.get('access_token')

        return response

    def get_page(self, path, return_content=True, return_html=True):
        response = self._telegraph.method('getPage', path=path, values={
            'return_content': return_content
        })

        if return_content and return_html:
            response['content'] = nodes_to_html(response['content'])

        return response

    def create_page(self, title, content=None, html_content=None,
                    author_name=None, author_url=None, return_content=False):
        if content is None:
            content = html_to_nodes(html_content)

        content_json = json.dumps(content, ensure_ascii=False)

        return self._telegraph.method('createPage', values={
            'title': title,
            'author_name': author_name,
            'author_url': author_url,
            'content': content_json,
            'return_content': return_content
        })

    def edit_page(self, path, title, content=None, html_content=None,
                  author_name=None, author_url=None, return_content=False):
        if content is None:
            content = html_to_nodes(html_content)

        content_json = json.dumps(content, ensure_ascii=False)

        return self._telegraph.method('editPage', path=path, values={
            'title': title,
            'author_name': author_name,
            'author_url': author_url,
            'content': content_json,
            'return_content': return_content
        })

    def get_account_info(self, fields=None):
        return self._telegraph.method('getAccountInfo', {
            'fields': json.dumps(fields, ensure_ascii=False) if fields else None
        })

    def get_page_list(self, offset=0, limit=50):
        return self._telegraph.method('getPageList', {
            'offset': offset,
            'limit': limit
        })

    def get_views(self, path, year=None, month=None, day=None, hour=None):
        return self._telegraph.method('getViews', path=path, values={
            'year': year,
            'month': month,
            'day': day,
            'hour': hour
        })
