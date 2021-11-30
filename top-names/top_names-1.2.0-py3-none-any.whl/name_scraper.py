'''Module containing the NameScraper class.'''
import requests
from bs4 import BeautifulSoup

class NameScraper:

    """
    Iterator that takes a site, scrapes it for names, and iterates through the names.
    """

    def __init__(self, site: str):
        self.site = site
        self.__rows = None
        self.__soup = None
        self.__i = None
        self.__dual = None

    @property
    def site(self) -> str:
        '''Return the site the scraper is working on.'''
        return self.__site

    @site.setter
    def site(self, site: str) -> str:
        '''Set the site for the scraper to work on.'''
        if not isinstance(site, str):
            raise TypeError(f"Expected site to be of type str, not type {site.__class__.__name__}.")
        self.__site = site

    @property
    def soup(self):
        '''The bs4 soup'''
        return self.__soup

    def __request(self):
        request = requests.get(self.site)
        if request.status_code == 200: # valid response
            self.__soup = BeautifulSoup(request.content, features="html.parser")
        else:
            raise RuntimeError(f"Received status code {request.status_code} from site.")

    def __process(self):
        table = self.__soup.find('table', class_='t-stripe')
        tbody = table.find('tbody')
        self.__rows = tbody.find_all('tr')
        del self.__rows[-1] # don't need the last row

    def __iter__(self):
        if self.__rows is None:
            self.__request()
            self.__process()
        self.__i = 0
        self.__dual = False
        return self

    def __next__(self):
        if self.__i >= len(self.__rows):
            raise StopIteration
        tr = self.__rows[self.__i]
        cells = tr.find_all('td')
        if self.__dual:
            self.__dual = False
            self.__i += 1
            return cells[3].get_text()
        else:
            self.__dual = True
            return cells[1].get_text()
