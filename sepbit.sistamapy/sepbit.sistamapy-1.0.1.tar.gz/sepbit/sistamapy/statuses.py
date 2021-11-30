'''
Sistamapy - Simple statuses Mastodon for Python
Copyright (C) 2020 Vitor Guia

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

class Statuses(object):
    '''
    Mastodon statuses
    See https://docs.joinmastodon.org/methods/statuses
    '''
    def __init__(self, instance, token):
        '''
        Mastodon statuses post
        '''
        self.instance = instance
        self.token = token


    def post(self, data):
        '''
        Mastodon post statuses
        '''
        data = urlencode(data)
        data = data.encode('ascii') # data should be bytes

        req = Request(
            'https://' + self.instance + '/api/v1/statuses',
            data,
            headers={
                'Content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Bearer ' + self.token
            },
            method='POST'
        )
        with urlopen(req) as res:
            res = res.read()

        return json.loads(res)


    def get(self, s_id):
        '''
        Mastodon get statuses
        '''
        req = Request(
            'https://' + self.instance + '/api/v1/statuses/' + str(s_id),
            headers={
                'Authorization': 'Bearer ' + self.token
            },
            method='GET'
        )
        with urlopen(req) as res:
            res = res.read()

        return json.loads(res)


    def delete(self, s_id):
        '''
        Mastodon delete statuses
        '''
        req = Request(
            'https://' + self.instance + '/api/v1/statuses/' + str(s_id),
            headers={
                'Authorization': 'Bearer ' + self.token
            },
            method='DELETE'
        )
        with urlopen(req) as res:
            res = res.read()

        return json.loads(res)
