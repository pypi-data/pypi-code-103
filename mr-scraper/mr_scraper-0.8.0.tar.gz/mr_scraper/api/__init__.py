import importlib
from typing import Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from webpilot import config, robot
from webpilot.robot import Robot

from mr_scraper.api.models import ContentProvider, ScraperConfig, QueryConfig, ScraperMessage

PUPPETEER_CHROME_PATH = 'chromium-browser'
PUPPETEER_HEADLESS = False
PUPPETEER_SANDBOXED = True
PUPPETEER_ROBOT: List[Optional[Robot]] = [None]

GetContent = Callable[[ContentProvider, str, dict], str]
Dispatch = Callable[[ScraperMessage], any]


class ApiReleaser:
    def __enter__(self):
        print("Enter PuppeteerRelease")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("Exit PuppeteerRelease")
        end()


def begin():
    pilot_config = config.WebPilotConfig(
        headless=PUPPETEER_HEADLESS,
        sandboxed=PUPPETEER_SANDBOXED,  # this is because collab run with root
        remote_port=33333,
        chrome_executable=PUPPETEER_CHROME_PATH)
    PUPPETEER_ROBOT[0] = robot.open_chrome(pilot_config)
    return ApiReleaser()


def end():
    if PUPPETEER_ROBOT[0] is not None:
        PUPPETEER_ROBOT[0].close()
        PUPPETEER_ROBOT[0] = None


def get_content_using_request(url: str, payload: dict, delay: int = 0) -> str:
    return requests.request("GET", url, payload).text


def get_content_using_puppeteer(url: str, payload: dict, delay: int = 0) -> str:
    with PUPPETEER_ROBOT[0].new_tab() as tab:
        page = tab.navigate(url, delay)
        return page.get_content()


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

    result = visit_dom(cfg, content)

    if cfg.callback is not None:
        return cfg.callback(result, message)

    return result


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
