import json
import ssl

from django.conf import settings
from urllib import parse, request

from flavius_api.conf import conf


class FlaviusBase:
    """
    FlaviusのAPIを取り扱うための基底クラス
    """
    endpoint = conf.FLAVIUS_ENDPOINT
    endpoint_dev = conf.FLAVIUS_ENDPOINT_DEV

    def __init__(self, search_url=None, create_url=None, update_url=None, delete_url=None):
        url = self.endpoint
        if settings.DEBUG:
            self.ssl_ctx = None
            url = self.endpoint_dev
        else:
            self.ssl_ctx = None
            url = self.endpoint
            # self.ssl_ctx = ssl.create_default_context()
            # self.ssl_ctx.load_cert_chain(certfile=conf.FLAVIUS_CRT_FILE,
            #                              keyfile=conf.FLAVIUS_KEY_FILE)

        self.search_url = url + search_url + self.make_get_parameter()
        self.create_url = url + create_url + self.make_get_parameter()
        self.update_url = url + update_url + self.make_get_parameter()
        self.delete_url = url + delete_url + self.make_get_parameter()

    @staticmethod
    def make_data(query=None):
        if query is None:
            query = dict()
        return parse.urlencode(query=query, doseq=True).encode()

    @staticmethod
    def make_request_headers(content_length=0):
        return {'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': content_length}

    def request(self, headers=None, func='search'):
        if headers is None:
            headers = self.make_request_headers(0)

        url = self.search_url
        if func == 'search':
            url = self.search_url
        elif func == 'create':
            url = self.create_url
        elif func == 'update':
            url = self.update_url
        elif func == 'delete':
            url = self.delete_url

        return request.Request(url=url, headers=headers, method='POST')

    @staticmethod
    def make_get_parameter():
        return '?regi=' + conf.FLAVIUS_API_REGI + '&staff=' + conf.FLAVIUS_API_STAFF

    def create(self, query=None):
        query = self.make_data(query=query)
        headers = self.make_request_headers(len(query))
        req = self.request(headers=headers, func='create')

        with request.urlopen(req, data=query, context=self.ssl_ctx) as response:
            return json.loads(response.read().decode('utf-8'))

    def edit(self, query=None):
        query = self.make_data(query=query)
        headers = self.make_request_headers(len(query))
        req = self.request(headers=headers, func='update')

        with request.urlopen(req, data=query, context=self.ssl_ctx) as response:
            return json.loads(response.read().decode('utf-8'))

    def search(self, query=None):
        query = self.make_data(query=query)
        headers = self.make_request_headers(len(query))
        req = self.request(headers=headers, func='search')

        with request.urlopen(req, data=query, context=self.ssl_ctx) as response:
            return json.loads(response.read().decode('utf-8'))

    def delete(self, query=None):
        query = self.make_data(query=query)
        headers = self.make_request_headers(len(query))
        req = self.request(headers=headers, func='delete')

        with request.urlopen(req, data=query, context=self.ssl_ctx) as response:
            return json.loads(response.read().decode('utf-8'))


class FlaviusBackData(FlaviusBase):
    """
    Flaviusのbackdataテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusBackData, self).__init__(search_url=conf.FLAVIUS_API_BACKDATA_SEARCH,
                                              create_url='', update_url='', delete_url='')


class FlaviusDto(FlaviusBase):
    """
    Flaviusの汎用的なAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusDto, self).__init__(search_url=conf.FLAVIUS_API_DTO_LIST,
                                         create_url='', update_url='', delete_url='')


class FlaviusDtoFetch(FlaviusBase):
    def __init__(self):
        super(FlaviusDtoFetch, self).__init__(search_url=conf.FLAVIUS_API_DTO_FETCH,
                                              create_url='', update_url='', delete_url='')


class FlaviusItem(FlaviusBase):
    """
    Flaviusのitemテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusItem, self).__init__(search_url=conf.FLAVIUS_API_ITEM_SEARCH,
                                          create_url=conf.FLAVIUS_API_ITEM_CREATE,
                                          update_url=conf.FLAVIUS_API_ITEM_EDIT,
                                          delete_url='')


class FlaviusEnvironment(FlaviusBase):
    """
    Flaviusのenvironmentテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusEnvironment, self).__init__(search_url=conf.FLAVIUS_API_ENVIRONMENT_SEARCH,
                                                 create_url=conf.FLAVIUS_API_ENVIRONMENT_SET,
                                                 update_url=conf.FLAVIUS_API_ENVIRONMENT_SET,
                                                 delete_url='')


class FlaviusSort(FlaviusBase):
    """
    Flaviusのsortテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusSort, self).__init__(search_url=conf.FLAVIUS_API_SORT_SEARCH,
                                          create_url='', update_url='', delete_url='')


class FlaviusHeader(FlaviusBase):
    """
    Flaviusのheaderテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusHeader, self).__init__(search_url=conf.FLAVIUS_API_HEADER_FETCH,
                                            create_url='', update_url='', delete_url='')

    def search(self, query=None):
        self.search_url += parse.urlencode(query=query, doseq=True)

        return super(FlaviusHeader, self).search(query=query)


class FlaviusData(FlaviusBase):
    """
    Flaviusのdataテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusData, self).__init__(search_url='', create_url=conf.FLAVIUS_API_DATA_CREATE,
                                          update_url=conf.FLAVIUS_API_DATA_UPDATE,
                                          delete_url=conf.FLAVIUS_API_DATA_DELETE)


class FlaviusPage(FlaviusBase):
    """
    Flaviusのpageテーブルに関連するAPIを実行するクラス
    """
    def __init__(self):
        super(FlaviusPage, self).__init__(search_url=conf.FLAVIUS_API_PAGE_FETCH,
                                          create_url='', update_url='', delete_url='')


class FlaviusOrderDecide(FlaviusBase):
    """
    Flaviusのオーダー送信を実行するAPI
    """
    def __init__(self):
        super(FlaviusOrderDecide, self).__init__(search_url='', create_url='', update_url=conf.FLAVIUS_API_ORDER_DECIDE,
                                                 delete_url='')


class FlaviusCreditAdd(FlaviusBase):
    """
    Flaviusの支払明細を追加するAPI
    """
    def __init__(self):
        super(FlaviusCreditAdd, self).__init__(search_url='', create_url=conf.FLAVIUS_API_CREDIT_ADD, update_url='',
                                               delete_url='')


class FlaviusPaymentComplete(FlaviusBase):
    """
    Flaviusの売上伝票を完了するAPI
    """
    def __init__(self):
        super(FlaviusPaymentComplete, self).__init__(search_url='', create_url='',
                                                     update_url=conf.FLAVIUS_API_PAYMENT_COMPLETE,
                                                     delete_url='')
