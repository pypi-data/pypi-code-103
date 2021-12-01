import parsel


def parse_product_ids(html: str) -> list:
    sel = parsel.Selector(text=html)
    product_ids = sel.xpath("//a[@data-listing-id]/@data-listing-id").getall()
    return product_ids
