from dataclasses import dataclass
from typing import Union

from bs4 import BeautifulSoup

from kabutobashi.domain.entity import StockDataSingleDay

from .page import Page, PageDecoder


@dataclass(frozen=True)
class StockInfoPage(Page):
    """

    Examples:
        >>> sip = StockInfoPage(code="0001")
        >>> result = sip.get()
    """

    code: Union[int, str]
    base_url: str = "https://minkabu.jp/stock/{code}"

    def url(self) -> str:
        return self.base_url.format(code=self.code)

    def _get(self) -> dict:
        soup = BeautifulSoup(self.get_url_text(url=self.url()), features="lxml")
        result = {}

        stock_board_tag = "ly_col ly_colsize_7 md_box ly_row ly_gutters"

        # ページ上部の情報を取得
        stock_board = soup.find("div", {"class": stock_board_tag})
        result.update(
            {
                "stock_label": PageDecoder(tag1="div", class1="stock_label").decode(bs=stock_board),
                "name": PageDecoder(tag1="p", class1="md_stockBoard_stockName").decode(bs=stock_board),
                "close": PageDecoder(tag1="div", class1="stock_price").decode(bs=stock_board),
                "date": PageDecoder(tag1="h2", class1="stock_label fsl").decode(bs=stock_board),
            }
        )

        # ページ中央の情報を取得
        stock_detail = soup.find("div", {"class": "stock-detail"})
        info = {}
        for li in stock_detail.find_all("li", {"class": "ly_vamd"}):
            info[li.find("dt").get_text()] = li.find("dd").get_text()
        result.update(
            {
                "industry_type": PageDecoder(tag1="div", class1="ly_content_wrapper size_ss").decode(bs=stock_detail),
                "open": info["始値"],
                "high": info["高値"],
                "low": info["安値"],
                "unit": info["単元株数"],
                "per": info["PER(調整後)"],
                "psr": info["PSR"],
                "pbr": info["PBR"],
                "volume": info["出来高"],
                "market_capitalization": info["時価総額"],
                "issued_shares": info["発行済株数"],
            }
        )
        return StockDataSingleDay.from_page_of(data=result).dumps()
