from dataclasses import dataclass

from bs4 import BeautifulSoup

from kabutobashi.domain.entity import Weeks52HighLow
from kabutobashi.errors import KabutobashiPageError

from .page import Page, PageDecoder


@dataclass(frozen=True)
class Weeks52HighLowPage(Page):
    data_type: str
    base_url: str = "https://jp.tradingview.com/markets/stocks-japan"

    def __post_init__(self):
        if self.data_type not in ["high", "low", "newly_high", "newly_low"]:
            raise KabutobashiPageError()

    def url(self) -> str:
        prefix = None
        # 52週の高値・底値を取得する関数とURL
        if self.data_type == "high":
            prefix = "highs-and-lows-52wk-high"
        elif self.data_type == "low":
            prefix = "highs-and-lows-52wk-low"
        elif self.data_type == "newly_high":
            prefix = "highs-and-lows-ath"
        elif self.data_type == "newly_low":
            prefix = "highs-and-lows-atl"

        if prefix is None:
            raise KabutobashiPageError()

        return f"{self.base_url}/{prefix}"

    @staticmethod
    def _crawl_volatility_info(table: BeautifulSoup, volatility_up_tag: str, volatility_down_tag: str) -> dict:
        # 上がったか、下がったかを判断するリスト
        evaluate_list = list()
        evaluate_list.extend(table.find_all("td", class_=volatility_up_tag))
        evaluate_list.extend(table.find_all("td", class_=volatility_down_tag))
        return Weeks52HighLowPage._volatility_replace_method(volatility_list=evaluate_list)

    @staticmethod
    def _volatility_replace_method(volatility_list: list) -> dict:
        """
        volatility_listにはweb pageから取得したデータが入っている
        suffixには高値か底値かを表す接頭辞を表す
        """
        if len(volatility_list) == 0:
            return {}
        ratio_candidate = volatility_list[0].text.replace("%", "")
        value_candidate = volatility_list[1].text
        return {"volatility_ratio": ratio_candidate, "volatility_value": value_candidate}

    def _get(self) -> dict:
        res = BeautifulSoup(self.get_url_text(url=self.url()), features="lxml")

        # ここからcrawlするページのタグ
        cell = "tv-screener-table__cell"
        signal = "tv-screener-table__signal"
        close_tag = f"tv-data-table__cell {cell} {cell}--big"
        # タグ
        volatility_up_tag = f"{close_tag} {cell}--up"
        volatility_down_tag = f"{close_tag} {cell}--down"
        buy_tag = f"{signal} {signal}--buy"
        strong_buy_tag = f"{signal} {signal}--strong-buy"
        sell_tag = f"{signal} {signal}--sell"
        strong_sell_tag = f"{signal} {signal}--strong-sell"

        content = res.find("tbody", class_="tv-data-table__tbody")
        table = content.find_all("tr")
        whole_result = []
        for t in table:
            volatility_dict = self._crawl_volatility_info(
                table=t, volatility_up_tag=volatility_up_tag, volatility_down_tag=volatility_down_tag
            )

            data = {
                "code": PageDecoder(tag1="a").decode(bs=t),
                "brand_name": PageDecoder(tag1="span").decode(bs=t),
                "close": PageDecoder(tag1="td", class1=close_tag).decode(bs=t),
                "volatility_up": PageDecoder(tag1="td", class1=volatility_up_tag).decode(bs=t),
                "volatility_down": PageDecoder(tag1="td", class1=volatility_down_tag).decode(bs=t),
                "buy": PageDecoder(tag1="span", class1=buy_tag).decode(bs=t),
                "strong_buy": PageDecoder(tag1="span", class1=strong_buy_tag).decode(bs=t),
                "sell": PageDecoder(tag1="span", class1=sell_tag).decode(bs=t),
                "strong_sell": PageDecoder(tag1="span", class1=strong_sell_tag).decode(bs=t),
                "volatility_ratio": volatility_dict.get("volatility_ratio", "-"),
                "volatility_value": volatility_dict.get("volatility_value", "-"),
            }
            whole_result.append(Weeks52HighLow.from_page_of(data=data).dumps())

        return {"weeks_52_high_low": whole_result}
