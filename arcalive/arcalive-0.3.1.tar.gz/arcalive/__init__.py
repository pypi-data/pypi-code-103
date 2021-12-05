__author__ = "SZI"
__copyright__ = "Copyright (c) 2021-2021 SZI"
# Use of this source code is governed by the MIT license.
__license__ = "MIT"

import requests
from bs4 import BeautifulSoup


class Error(Exception):
    pass


class ArcaError(Error):
    def __init__(self, message):
        self.message = message


class ArcaAPI():
    curSession = requests.Session()

    def __init__(self, **kwargs):
        logined = False
        self.kwarg = kwargs

    def Csrf_get(self, URL):
        html = self.curSession.get(URL, **self.kwarg)
        soup = BeautifulSoup(html.text, 'html.parser')
        csrf = ''
        token = ''
        try:
            csrf = soup.find("input", {"name": "_csrf"}).attrs['value']
            try:
                token = soup.find("input", {"name": "token"}).attrs['value']
            except:
                pass
        except:
            try:
                form = (soup.find('form', id='commentForm'))
                csrf = (form.find('input').attrs['value'])
            except:
                csrf = str(soup.find("a", "subscribe-btn").attrs['href']).split('_csrf=')[1]
        return [csrf, token]

    def check_for_error(self, a):
        raise_error = []
        try:
            soup = BeautifulSoup(a.text, 'html.parser')
            rul = soup
            raise_error = rul
        except:
            pass
        if len(raise_error) > 0:
            h4s = raise_error.find_all('h4')
            for u in h4s:
                if (u.encode_contents()) == b'\xf0\x9f\x98\xb1 \xec\x98\xa4\xeb\xa5\x98':
                    h4s = raise_error.find_all('p')
                    raise ArcaError(h4s[0].encode_contents().decode('utf-8'))

        if a.status_code == 404:
            raise ArcaError('target dosen\'t exist')
        if a.status_code == 403:
            raise ArcaError('You do not have permission')
        if a.status_code == 428:
            raise ArcaError('You need Login')
        if a.status_code > 202:
            raise ArcaError('HTML ERROR ' + str(a.status_code))

    def login(self, id, password):
        URL = 'https://arca.live/u/login'
        payload = {'username': id, 'password': password, 'goto': '/', '_csrf': self.Csrf_get(URL)[0]}
        a = self.curSession.post(URL, data=payload)
        self.check_for_error(a)
        self.logined = True

    def delete_post(self, id):
        id = str(id)
        URL = 'https://arca.live/b/chan/' + id + '/delete'
        payload = {'_csrf': self.Csrf_get(URL)[0]}
        a = self.curSession.post(URL, data=payload)
        self.check_for_error(a)

    def delete_comment(self, pid, id):
        id = str(id)
        pid = str(pid)
        URL = 'https://arca.live/b/chan/' + pid + '/' + id + '/delete'
        payload = {'_csrf': self.Csrf_get(URL)[0]}
        a = self.curSession.post(URL, data=payload)
        self.check_for_error(a)

    def post_article(self, channel, name, content, category=None, copy_humor=False, agree_prevent_delete=False):
        URL = 'https://arca.live/b/' + channel + '/write'
        csrf = self.Csrf_get(URL)
        payload = {'_csrf': csrf[0],
                   'token': csrf[1],
                   'contentType': 'html',
                   'category': category,
                   'title': name,
                   'content': content,
                   }
        if copy_humor:
            payload['copyHumorArticle'] = 'on'
        if agree_prevent_delete:
            payload['agreePreventDelete'] = 'on'
        a = self.curSession.post(URL, data=payload)
        self.check_for_error(a)

    def get_channel_info(self, channel):
        response = {}
        URL = 'https://arca.live/b/' + channel
        html = self.curSession.get(URL, **self.kwarg)
        self.check_for_error(html)
        soup = BeautifulSoup(html.text, 'html.parser')
        sh = soup.find_all('div', 'board-title')  # 채널 이름 구하기
        response['name'] = ''
        for y in sh:
            try:
                x = y.find_all('a')[1]
                if x.attrs['href'] == '/b/' + channel:
                    response['name'] = x.text
                    break
            except:
                pass

        sh = soup.find('div', 'desc')
        response['subscribe'] = int(sh.text.replace('구독자', '').replace('명', '').replace(' ', '').replace('\n', ''))
        sh = soup.find('div', 'desc user-info')
        try:
            response['juddak'] = (sh.text.replace('\n', ''))
        except:
            response['juddak'] = ''

        sh = soup.find_all('ul', 'board-category')[0].find_all('a')  # 글머리 구하기
        response['category'] = []
        for x in range(len(sh)):
            y = ({'display_name': sh[x].text, 'name': sh[x].attrs['href'].replace('/b/' + channel, '')})
            if len(y['name']) > 0:
                y['name'] = y['name'].replace('?category=', '')
                response['category'].append(y)
        return response

    def get_channel_article(self, channel, page=1, best=False, category=None, cut_rate=None, sort=None, search=None,
                            search_target=None):
        URL = 'https://arca.live/b/' + channel + '?p=' + str(page)
        if best:
            URL += '&mode=best'
        if search is not None:
            URL += '&keyword=' + search
            if search_target is None:
                URL += '&target=' + 'all'
        if search_target is not None:
            if not search_target in ['all', 'title_content', 'title', 'content', 'nickname']:
                raise ArcaError('search_target must be one of: "all","title_content","title","content","nickname"')
            URL += '&target=' + search_target
            if search is None:
                raise ArcaError('search must be defined')
        if category is not None:
            URL += '&category=' + category
        if cut_rate is not None:
            URL += '&cut=' + str(cut_rate)
        if sort is not None:
            sorts = ['rating', 'rating72', 'ratingAll', 'commentCount', 'recentComment']
            if not sort in sorts:
                raise ArcaError('sort is must be in ' + str(sorts))
            else:
                URL += '&sort=' + sort
        html = self.curSession.get(URL, **self.kwarg)
        soup = BeautifulSoup(html.text, 'html.parser')
        a = soup.find_all('a', 'vrow')
        response = {}
        response['posts'] = []
        response['notice'] = []

        for x in a:
            post = {}
            soup2 = BeautifulSoup(str(x), 'html.parser')
            try:
                post_id = str(x.attrs['href'])
                try:
                    post_id = post_id.split('/')[3]
                    if '?' in post_id:
                        post_id = post_id.split('?')[0]
                except:
                    pass
                post['id'] = int(post_id)
                post_num = soup2.find('span', 'vcol col-id').text.replace('\n', '')
                post['number'] = post_num
                post['name'] = (soup2.find('span', 'vcol col-title').text.replace('\n', ''))
                post['user'] = soup2.find('span', 'user-info').find('span').attrs['data-filter']
                post['time'] = (soup2.find('time').attrs['datetime'])
                post['view'] = int(soup2.find('span', 'vcol col-view').text.replace('\n', '').replace(' ', ''))
                try:
                    post['rate'] = int(
                        soup2.find('span', 'vcol col-rate d-none d-sm-inline').text.replace('\n', '').replace(' ', ''))
                except:
                    post['rate'] = 0
                if post_num == '공지':
                    response['notice'].append(post)
                    post['number'] = 0
                else:
                    try:
                        post['name'] = (soup2.find('span', 'title ion-android-star').text.replace('\n', ''))
                    except:
                        post['name'] = (soup2.find('span', 'title').text.replace('\n', ''))
                    post['rate'] = int(soup2.find('span', 'vcol col-rate').text.replace('\n', ''))
                    post['view'] = int(soup2.find('span', 'vcol col-view').text.replace('\n', ''))
                    try:
                        post['comments'] = int(
                            soup2.find('span', 'comment-count').text.replace('\n', '').replace('[', '').replace(']',
                                                                                                                ''))
                    except:
                        post['comments'] = 0
                    response['posts'].append(post)
            except Exception as e:
                pass
        return response

    def get_article(self, id):
        response = {}
        URL = 'https://arca.live/b/a/' + str(id)
        html = self.curSession.get(URL, **self.kwarg)
        self.check_for_error(html)
        soup = BeautifulSoup(html.text, 'html.parser')
        asoup = soup.find('div', 'article-head')
        response['name'] = (asoup.find('div', 'title').text.replace('\n', ''))
        info = soup.find('div', 'article-info').find_all('span', 'body')
        response['info'] = {}
        response['info']['like'] = int(info[0].text)
        response['info']['dislike'] = int(info[1].text)
        response['info']['comments'] = int(info[2].text)
        response['info']['views'] = int(info[3].text)
        response['info']['created'] = (info[4].find('time').attrs['datetime'])
        try:
            response['info']['edited'] = (info[5].find('time').attrs['datetime'])
        except:
            pass
        try:
            response['info']['category'] = asoup.find('div', 'title').find('span', 'badge badge-success').text
            response['name'] = response['name'][len(response['info']['category']):]
        except:
            pass
        comments = soup.find_all('div', 'comment-wrapper')
        response['comment'] = []
        for x in comments:
            comment = {}
            try:
                comment['text'] = x.find('div', 'text').text
            except:
                try:
                    comment['text'] = (x.find('img', 'emoticon').attrs['src'])
                except:
                    pass
            try:
                comment['user'] = x.find('span', 'user-info').find('a').attrs['data-filter']
            except:
                try:
                    comment['user'] = x.find('span', 'user-info').find('span').attrs['data-filter']
                except:
                    pass
            comment['comment_id'] = (int(x.attrs['id'].replace('c_', '')))
            response['comment'].append(comment)
        response['content'] = (soup.find('div', 'fr-view article-content'))
        return response

    def post_comment(self, id, message, reply_to=None):
        URL = 'https://arca.live/b/maplete/' + str(id)
        html = self.curSession.get(URL, **self.kwarg)
        self.check_for_error(html)
        csrf = self.Csrf_get(URL)[0]
        payload = {'_csrf': csrf,
                   'contentType': 'text',
                   'content': message,
                   'parentId': reply_to
                   }
        a = self.curSession.post(URL + '/comment', data=payload)
        self.check_for_error(a)

    def like(self, id, dislike=False):
        URL = 'https://arca.live/b/maplete/' + str(id)
        html = self.curSession.get(URL, **self.kwarg)
        idurl = html.url.split('/')
        idurl = idurl[len(idurl) - 2:][0] + '/' + idurl[len(idurl) - 2:][1]
        self.check_for_error(html)
        csrf = self.Csrf_get(URL)[0]
        like = 1
        if dislike:
            like = -1
        payload = {'_csrf': csrf,
                   'value': like
                   }
        a = self.curSession.post('https://arca.live/api/rate/' + idurl, data=payload)
        self.check_for_error(a)
