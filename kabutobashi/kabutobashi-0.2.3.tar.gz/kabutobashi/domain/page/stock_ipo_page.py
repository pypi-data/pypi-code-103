from dataclasses import dataclass
from typing import Union

from bs4 import BeautifulSoup

from kabutobashi.domain.entity import StockIpo

from .page import Page


@dataclass(frozen=True)
class StockIpoPage(Page):
    year: Union[str, int]
    base_url: str = "https://96ut.com/ipo/list.php"

    def url(self) -> str:
        if type(self.year) is int:
            year = str(self.year)
        else:
            year = self.year
        return f"{self.base_url}?year={year}"

    def _get(self) -> dict:
        res = BeautifulSoup(self.get_url_text(url=self.url()), features="lxml")
        table_content = res.find("div", {"class": "tablewrap"})
        table_thead = table_content.find("thead")
        # headの取得
        table_head_list = []
        for th in table_thead.find_all("th"):
            table_head_list.append(th.get_text())

        # bodyの取得
        table_tbody = table_content.find("tbody")
        whole_result = []
        for idx, tr in enumerate(table_tbody.find_all("tr")):
            table_body_dict = {}
            for header, td in zip(table_head_list, tr.find_all("td")):
                table_body_dict[header] = td.get_text().replace("\n", "")
            whole_result.append(StockIpo.from_page_of(data=table_body_dict).dumps())
        return {"ipo_list": whole_result}
