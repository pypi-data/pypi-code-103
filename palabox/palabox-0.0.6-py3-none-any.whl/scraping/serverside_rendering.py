"""Scraping for serverside rendering."""

from typing import Optional

import requests

from .clean_html import clean_html_to_text


def scrap_one_website(url: str, session: Optional[requests.Session] = None) -> str:
    """Scrap one website."""
    if session is None:
        content: str = requests.get(url).content.decode()
    else:
        content = session.get(url).content.decode()
    return content


if __name__ == "__main__":
    _ = scrap_one_website("https://marco.boucas.fr/")
    with open("test.txt", "w", encoding="utf-8") as file:
        file.write(_)
    _ = clean_html_to_text(_)
    with open("test2.txt", "w", encoding="utf-8") as file:
        file.write(_)
