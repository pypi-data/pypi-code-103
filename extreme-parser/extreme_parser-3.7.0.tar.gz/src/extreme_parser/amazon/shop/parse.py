import parsel

from extreme_parser.amazon.shop.model import Shop
from extreme_parser.util.parse import parse_number


def parse(html: str, s: Shop):
    sel = parsel.Selector(text=html)
    parse_seller(s, selector=sel)
    parse_name(s, selector=sel)
    parse_address(s, selector=sel)
    parse_stars(s, selector=sel)
    parse_ratings(s, selector=sel)


def parse_seller(s: Shop, selector: parsel.Selector = None):
    s.seller = selector.xpath("//*[@id='sellerName']/text()").get()


def parse_name(s: Shop, selector: parsel.Selector = None):
    s.name = selector.xpath("//span[contains(text(), 'Business Name')]/following-sibling::text()").get()


def parse_address(s: Shop, selector: parsel.Selector = None):
    address = selector.xpath("//span[contains(text(), 'Business Address')]/following-sibling::ul/li//text()").getall()
    address = " ".join(address)
    if address == "":
        s.address = None
    else:
        s.address = address


def parse_stars(s: Shop, selector: parsel.Selector = None):
    stars = selector.xpath("//i[contains(@class, 'feedback-detail-stars')]/span/text()").get()
    if stars is None:
        s.stars = None
    else:
        s.stars = parse_number(stars)


def parse_ratings(s: Shop, selector: parsel.Selector = None):
    ratings = selector.xpath("//a[contains(@class, 'feedback-detail-description')]/text()").re_first(r"(\d+) rating")
    if ratings is None:
        s.ratings = None
    else:
        s.ratings = int(ratings)
