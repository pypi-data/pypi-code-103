from typing import List

import parsel

from extreme_parser.amazon.option.model import Option


def parse(html: str) -> List[Option]:
    blocks = parsel.Selector(text=html).xpath("//div[@id='aod-offer']")
    options = list()
    for b in blocks:
        o = Option()
        parse_sold(o, b)
        parse_sold_url_rel(o, b)
        options.append(o)
    return options


def parse_sold(o: Option, block: parsel.Selector):
    sold = block.xpath("//div[@id='aod-offer-soldBy']//a/text()").get()
    if sold is None:
        o.sold = None
    else:
        o.sold = sold.strip()


def parse_sold_url_rel(o: Option, block: parsel.Selector):
    sold_url_rel = block.xpath("//div[@id='aod-offer-soldBy']//a/@href").get()
    if sold_url_rel is None:
        o.sold_url_rel = None
    else:
        o.sold_url_rel = sold_url_rel
