import sys
import pydantic
from typing import List, Union, Optional, Callable
from abc import ABC, abstractmethod

sys.path.insert(1, '/app')

class AutoModel(pydantic.BaseModel):
    country: Optional[str] = 'usa'

class UrlPattern(ABC):
    @abstractmethod
    def url_strategy(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        """abstract base class for the url formation strategy pattern"""
        pass

class NullRadiusComponent(UrlPattern):
    def url_strategy(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={}&types=geocode&components&key={}'.format(
            address, token)
        return url

class PresentRadiusNullLocation(UrlPattern):
    def url_strategy(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={}&types=geocode&radius={}&components&key={}'.format(
            address, radius, token)
        return url

class OnlyRadiusPresent(UrlPattern):
    def url_strategy(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={}&types=geocode&location={}&components&key={}'.format(
            address, location, token)
        return url

class FillKnownsStrategy(UrlPattern):
    def url_strategy(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input={}&types=geocode&radius={}&key={}'.format(
            address, int(radius), token)
        return url

class OrganizeUrlStrategies:
    """organize/director class for url strategy formation"""
    def __init__(self, strategy: UrlPattern):
        self.strategy = strategy

    def create_url(self, address: str, token: str, location: List[Union[float, int]], radius: Union[float, int]) -> str:
        return self.strategy.url_strategy(address=address, token=token, location=location, radius=radius)

def main_urls(address: str, token: str, location: List[Union[float, int]], radius: Union[float, int], strategy: Callable, *args) -> str:
    """return the proper url per strategy"""
    UrlObject = OrganizeUrlStrategies(strategy)
    return UrlObject.create_url(address=address, token=token, location=location, radius=radius)