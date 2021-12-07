import importlib
from typing import Callable, Dict

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from pydantic.dataclasses import dataclass
from webpilot import config, robot

from mr_scraper.api.models import ContentProvider, ScraperConfig, QueryConfig

PUPPETEER_CHROME_PATH = 'chromium-browser'


@dataclass
class ScraperMessage:
    scraper: str
    type: str
    payload: Dict


GetContent = Callable[[ContentProvider, str, dict], str]
Dispatch = Callable[[ScraperMessage], any]


def get_content_using_request(url: str, payload: dict, delay: int = 0) -> str:
    return requests.request("GET", url, payload).text


def get_content_using_puppeteer(url: str, payload: dict, delay: int = 0) -> str:
    pilot_config = config.WebPilotConfig(
        headless=True,
        sandboxed=False,  # this is because collab run with root
        remote_port=33333,
        chrome_executable=PUPPETEER_CHROME_PATH)
    with robot.open_chrome(pilot_config) as pilot:
        tab = pilot.new_tab()
        page = pilot.navigate(tab, url, delay)
        return pilot.get_content(page)


__content_providers__ = {
    ContentProvider.REQUEST: get_content_using_request,
    ContentProvider.PUPPETEER: get_content_using_puppeteer
}


def get_content(provider: ContentProvider, url: str, payload: dict, delay: int = 0):
    return __content_providers__[provider](url, payload, delay=delay)


def dispatch(message: ScraperMessage):
    module = importlib.import_module(message.scraper)
    cfg: ScraperConfig = getattr(module, message.type)
    url = cfg.content.url(message.payload)
    content = get_content(cfg.content.provider, url, message.payload, delay=cfg.content.delay)

    return visit_dom(cfg, content)


def visit_dom(cfg: ScraperConfig, content: str):
    dom = BeautifulSoup(content, features="html.parser")
    return visit_dom_queries(dom, cfg.queries)


def visit_dom_queries(dom: Tag, queries: Dict[str, QueryConfig]):
    return {key: visit_dom_query(dom, value) for (key, value) in queries.items()}


def visit_dom_query(dom: Tag, value: QueryConfig):
    result = [dom_compound(value.transform(item), value.queries) for item in dom.select(value.selector)]

    if len(result) == 1:
        return result[0]
    return result


def dom_compound(value, queries: Dict[str, QueryConfig]):
    if queries is None:
        return value
    return visit_dom_queries(value, queries)
