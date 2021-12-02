import parsel

from extreme_parser.amazon.search.model import Search
from extreme_parser.util.parse import parse_number


def parse(html: str, search: Search):
    sel = parsel.Selector(text=html)
    parse_products(search, sel)
    parse_max_page(search, sel)
    parse_results(search, sel)
    parse_brands(search, sel)


def parse_products(search: Search, sel: parsel.Selector):
    products = sel.xpath("//@data-asin").getall()
    products = list(filter(lambda s: s != '', products))
    if len(products) == 0:
        search.products = None
    else:
        search.products = products


def parse_max_page(search: Search, sel: parsel.Selector):
    max_page = sel.xpath("//ul[@class='a-pagination']/li[last()-1]/text()").get()
    if max_page and max_page.isdigit():
        search.max_page = int(max_page)
    else:
        search.max_page = None


def parse_results(search: Search, sel: parsel.Selector):
    results = sel.xpath(
        'normalize-space(//span[@data-component-type="s-result-info-bar"]//span[contains(text(), "result")]/text())'
    ).get()
    if results == "":
        search.results = None
        return

    results = parse_number(results.replace(",", ""), first=False)
    if results is None or isinstance(results[-1], float):
        search.results = None
    else:
        search.results = results[-1]


def parse_brands(search: Search, sel: parsel.Selector):
    brands = sel.xpath("//div[@id='brandsRefinements']//a[@data-routing]/span/text()").getall()
    if len(brands) == 0:
        search.brands = None
    else:
        search.brands = brands
