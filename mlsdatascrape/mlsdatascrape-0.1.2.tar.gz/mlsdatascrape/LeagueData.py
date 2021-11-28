import requests as req
from bs4 import BeautifulSoup
from mlsdatascrape.Parser import Parser as Pars


class LeagueData:

    def __init__(self, season_year):
        self.season_year = season_year
        self.season_id_dict = {2021: 11006, 2020: 10090, 2019: 2798, 2018: 1759, 2017: 1558, 2016: 1503, 2015: 1369,
                               2014: 708, 2013: 643, 2012: 577, 2011: 509, 2010: 442, 2009: 374, 2008: 316, 2007: 260,
                               2006: 211, 2005: 168, 2004: 133, 2003: 100, 2002: 75, 2001: 56, 2000: 44, 1999: 37,
                               1998: 34, 1997: 32, 1996: 30}

    # get_eastern_conference_table - returns the eastern conference table
    def eastern_conference_table(self):
        """

        :rtype: list
        """

        # Set URL for MLS season
        url = ''

        if self.season_year in self.season_id_dict:
            url = 'https://fbref.com/en/comps/22/' + str(self.season_id_dict[self.season_year]) + '/' + str(
                self.season_year) + \
                  '-Major-League-Soccer-Stats'
        else:
            return ['No data for season']

        page = req.get(url)

        # parse URL using BS4 and get tables
        soup = BeautifulSoup(page.content, 'html.parser')
        table_obj = soup.find(id='results' + str(self.season_id_dict[self.season_year]) + '1Eastern-Conference_overall')

        return Pars(table_obj).parse_club_table()

    # get_western_conference_table - returns the western conference table
    def western_conference_table(self):
        """

        :rtype: list
        """

        # Set URL for MLS season
        url = ''

        if self.season_year in self.season_id_dict:
            url = 'https://fbref.com/en/comps/22/' + str(self.season_id_dict[self.season_year]) + '/' + \
                  str(self.season_year) + '-Major-League-Soccer-Stats'
        else:
            return ['No data for season']

        page = req.get(url)

        # parse URL using BS4 and get tables
        soup = BeautifulSoup(page.content, 'html.parser')
        table_obj = soup.find(id='results' + str(self.season_id_dict[self.season_year]) + '1Western-Conference_overall')

        return Pars(table_obj).parse_club_table()