import requests as rq

from . import utils, resources


class Client:
    BASE_URL = 'https://ws.fr.shopping.rakuten.com'

    def __init__(self, login, token):
        
        self._login = login
        self._token = token

        self._session = rq.Session()

        self._resources = {
            'categorymap': resources.CategoryMapResource(
                utils.urljoin(self.BASE_URL, 'categorymap_ws'), 
                self._session, 
                params={'action': 'categorymap', 'login': self._login, 'version': '2011-10-11'}
            ),
            'producttypes': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'stock_ws'), 
                self._session, 
                params={'action': 'producttypes', 'login': self._login, 'pwd': self._token, 'version': '2015-06-30'}
            ),
            'producttypetemplate': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'stock_ws'), 
                self._session, 
                params={'action': 'producttypetemplate', 'login': self._login, 'pwd': self._token, 'version': '2017-10-04'}
            ),
            'genericimportfile': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'stock_ws'), 
                self._session, 
                params={'action': 'genericimportfile', 'login': self._login, 'pwd': self._token, 'version': '2015-02-02'}
            ),
            'genericimportreport': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'stock_ws'), 
                self._session, 
                params={'action': 'genericimportreport', 'login': self._login, 'pwd': self._token, 'version': '2017-02-10'}
            ),
            'acceptsale': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'sales_ws'), 
                self._session, 
                params={'action': 'acceptsale', 'login': self._login, 'pwd': self._token, 'version': '2021-04-08'}
            ),
            'getnewsales': resources.ProductTypesResource(
                utils.urljoin(self.BASE_URL, 'sales_ws'), 
                self._session, 
                params={'action': 'getnewsales', 'login': self._login, 'pwd': self._token, 'version': '2017-08-07'}
            ),

        }

    @property
    def resources(self):
        return self._resources        

    @property
    def categorymap(self):
        return self.resources.get('categorymap')

    @property
    def producttypes(self):
        return self.resources.get('producttypes')

    @property
    def producttypetemplate(self):
        return self.resources.get('producttypetemplate')

    @property
    def genericimportfile(self):
        return self.resources.get('genericimportfile')

    @property
    def genericimportreport(self):
        return self.resources.get('genericimportreport')

    @property
    def acceptsale(self):
        return self.resources.get('acceptsale')

    @property
    def getnewsales(self):
        return self.resources.get('getnewsales')        