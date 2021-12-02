from typing import Union

import parsel

from extreme_parser.util.parse import parse_number


def parse_product_ids(html: str) -> list:
    sel = parsel.Selector(text=html)
    product_ids = sel.xpath("//a[@data-listing-id]/@data-listing-id").getall()
    return product_ids


def parse_sales(html: str) -> Union[int, None]:
    sel = parsel.Selector(text=html)
    sales = sel.xpath("//div[@class='hide-xs text-gray-lightest text-smaller ml-xs-2']/text()").get()
    if sales is None:
        return None
    else:
        return parse_number(sales)
