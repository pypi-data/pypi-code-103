import httpx
from pyquery import PyQuery
from urge.base import ProcManager
import typing as t

# from ..base import ProcManager


def get_weather(city, ascii_graphs: bool = True, lang: str = "en", **kwargs) -> dict:
    res = httpx.get(
        f'https://wttr.in/{city}?lang={lang}{ "&T0" if ascii_graphs else "&format=j1"}'
    )
    return dict(res=res, ascii_graphs=ascii_graphs)


def ret_weather(
    res: httpx.Response, ascii_graphs: bool, **kwargs
) -> t.Union[str, float]:
    if ascii_graphs:
        pq = PyQuery(res.text)
        result = pq.find("pre")
        return str(result.text(squash_space=False))
    temp = res.json().get("current_condition")
    return float(temp[0].get("FeelsLikeC"))


def get_now_temp(city: str, ascii_graphs: bool = True):
    p = ProcManager(get_weather, ret_weather)
    return p(dict(city=city, ascii_graphs=ascii_graphs))


def get_simple_temp(city: str):
    return int(get_now_temp(city, ascii_graphs=False))
