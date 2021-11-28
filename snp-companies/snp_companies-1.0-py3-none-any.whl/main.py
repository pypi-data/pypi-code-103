import re
from datetime import date, datetime
from typing import Union, List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd
from numpy import datetime64


class SNPListing(object):
    def __init__(self):
        self._ticker_changes = {
            "Q": "IQV",
            "KORS": "CPRI",
            "DLPH": "APTV",
            "IR": "TT",
            "PTV": "TT",
            "PCLN": "BKNG",
            "HRS": "LHX",
            "JEC": "J",
            "TSO": "ANDV",
            "LUK": "JEF",
            "KRFT": "KHC",
            "KFT": "KHC"
        }
        response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content.decode("utf8"), 'html.parser')
            current_state = self._get_current_state(soup)
            changes = self._get_all_changes(soup)
            self._list_per_date = self._prepare_list_per_date(current_state, changes)
        else:
            raise Exception(
                "Failed to fetch the data from https://en.wikipedia.org/wiki/List_of_S%26P_500_companies, try again later")

    def _get_current_state(self, soup: BeautifulSoup) -> pd.DataFrame:
        data = []
        try:
            all_table_lines = soup.find("table", id="constituents").find("tbody").find_all("tr")
            only_content_lines = all_table_lines[1:]
            for line in only_content_lines:
                cells = line.find_all("td")
                data.append({"Ticker": cells[0].text.strip(), "Security": cells[1].text.strip()})
        except:
            raise Exception("Failed to process the current s&p table, The library needs an update...")
        return pd.DataFrame(data)

    def _get_all_changes(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        data = []
        try:
            all_table_lines = soup.find("table", id="changes").find("tbody").find_all("tr")
            only_content_lines = all_table_lines[2:]
            for line in only_content_lines:
                cells = line.find_all("td")
                add_ticker = cells[1].text.strip()
                remove_ticker = cells[3].text.strip()
                change = {"Date": cells[0].text.strip(), "Add_Ticker": self._ticker_changes.get(add_ticker, add_ticker),
                          "Add_Security": cells[2].text.strip(),
                          "Remove_Ticker": self._ticker_changes.get(remove_ticker, remove_ticker),
                          "Remove_Security": cells[4].text.strip(),
                          "Reason": re.sub(r"\[[0-9]+\]", "", cells[5].text).strip()}
                data.append(change)
        except:
            raise Exception("Failed to process the changes table, The library needs an update...")
        return data

    def _prepare_list_per_date(self, current_list: pd.DataFrame, changes: List[Dict[str, str]]) -> List[dict]:
        current_date = changes[0]['Date']
        lst = current_list
        lists = [{"Date": pd.to_datetime(date.today()), "companies": lst.copy()}]
        for i, change in enumerate(changes):
            if current_date != change['Date']:
                lists.append({"Date": pd.to_datetime(current_date), "companies": lst.copy()})
                current_date = change['Date']
            if change["Remove_Ticker"] == change["Add_Ticker"]:
                continue
            if change["Remove_Ticker"]:
                # Because we're going backward, when something was removed, it means it was actually in beforehand.
                lst = lst.append({"Ticker": change["Remove_Ticker"], "Security": change["Remove_Security"]},
                                 ignore_index=True)
            if change["Add_Ticker"]:
                # Because we're going backward, when something was added, it means it wasn't actually in beforehand.
                lst = lst[lst['Ticker'] != change["Add_Ticker"]]
        lists.append({"Date": pd.to_datetime(current_date), "companies": lst.copy()})
        return lists

    def __getitem__(self, item: Union[str, datetime, datetime64]) -> pd.DataFrame:
        """
        :param item: Date string
        :return: DataFrame
        """
        try:
            parsed_date = pd.to_datetime(item)
        except:
            raise Exception(f"{item} is not a date format")
        if parsed_date < self._list_per_date[-1]["Date"]:
            raise Exception(f"The first date available is {self._list_per_date[-1]['Date']}")
        if parsed_date > pd.to_datetime(date.today()):
            raise Exception("Sorry, we don't know the future")
        for lst in reversed(self._list_per_date):
            if parsed_date < lst['Date']:
                return lst['companies']
