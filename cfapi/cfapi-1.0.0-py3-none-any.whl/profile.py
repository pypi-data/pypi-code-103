from .base import Base

import re
from urllib.parse import urljoin


class Profile(Base):

    _FROM_URL_REGEX = re.compile("/profile/(P?<profileid>[a-zA-Z]+)")

    @classmethod
    def identifier_from_url(cls, url: str) -> "Optional[str]":
        result = re.search(cls._FROM_URL_REGEX, url)
        if result:
            return result.group("profileid")

    @property
    def url(self) -> str:
        """The URL to the page where the information is scraped from."""
        return urljoin(self.BASE_URL, f"profile/{self.identifier}")

    @property
    def rank(self) -> str:
        return self.data.find("div", {"class": "user-rank"}).get_text().strip()

    @property
    def name(self) -> str:
        return (
            self.data.find("div", {"class": "main-info"}).find("h1").get_text().strip()
        )
