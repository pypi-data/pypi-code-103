import asyncio

import httpx
from selectolax.parser import HTMLParser
from yarl import URL

from ._dataclasses import Result


def anext(async_iterator):
    return async_iterator.__anext__()


def iter_over_async(ait, loop):
    ait = ait.__aiter__()

    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None

    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj


def search(query: str):
    """
    Searches :param:`query`
    """
    generator = Search(query)._iter_results()
    return generator


async def asearch(query: str):
    """
    Searches :param:`query`
    """
    generator = ResultAsyncGenerator(await Search(query)._aiter_results())
    return generator


class ResultAsyncGenerator:
    def __init__(self, iterator) -> None:
        self.iterator = iterator

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await anext(self.iterator)


class Search:
    def __init__(self, query: str):
        self.query = query.strip()
        self.url = URL("https://html.duckduckgo.com/html/")
        self.query_url = self.url.with_query(q=self.query)

    def _get_html(self):
        try:
            response = httpx.get(self.query_url.human_repr())
            return response.text
        except httpx.ConnectTimeout:
            raise ValueError("No results.") from None

    async def _async_get_html(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.query_url.human_repr())
                return response.text
        except httpx.ConnectTimeout:
            raise ValueError("No results.") from None

    def _iter_results(self):
        loop = asyncio.get_event_loop()
        html = self._get_html()
        return iter_over_async(self.get_results(html), loop)

    async def _aiter_results(self):
        html = await self._async_get_html()
        return self.get_results(html)

    async def get_results(self, html):
        parser = HTMLParser(html, True)
        results = parser.css_first("div.results")

        for result in results.css("div.result"):
            try:
                title = result.css_first("a.result__a")
                title_text = title.text()
                title_url = URL(title.attrs["href"]).query.get("uddg")
                description = result.css_first("a.result__snippet").text()
                icon_url = (
                    URL(result.css_first("img.result__icon__img").attrs["src"])
                    .with_scheme("https")
                    .human_repr()
                )
            except Exception:
                raise ValueError("No results.") from None
            yield Result(
                title=title_text,
                description=description,
                url=title_url,
                icon_url=icon_url,
            )
