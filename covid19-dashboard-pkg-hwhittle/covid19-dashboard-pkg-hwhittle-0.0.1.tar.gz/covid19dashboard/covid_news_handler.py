"""covid_news_handler

This module is used for everything related to fetching covid news articles

It exports the following functions
 * news_API_request(covid_terms: str)
    -> fetches news articles using newsapi based on given terms, separated by space
 * update_news()
    -> updates the news_articles array with new news articles using news_API_request
 * add_removed_article(article)
    -> This function adds an article to the removed list, preventing it from being
       displayed again.
 * remove_article_by_title(title)
    -> Removes an article from news_articles by the article's title.
 * schedule_news_updates(update_interval, update_name, repeat=False, absolute=False)
    -> Schedules a news update at the given interval with a given name.

It exports the following variables
 * news_articles : list[Article]
    -> a list of articles that have been filtered to not include removed articles
"""

from typing import Dict, List

import requests

from .config import get_config
from .logger import log_debug, log_info
from .scheduler import queue_task

news_articles: List[Dict] = []

# Using a map here would be faster, however it would also use more memory.
removed_articles: List[Dict] = []

def news_API_request(covid_terms = "Covid COVID-19 coronavirus") -> List[Dict]:
    """
    This function fetches news articles using newsapi based on the given search terms.

    Parameters
    ----------
    covid_terms : str
        default = "Covid COVID-19 coronavirus"
        This parameter is used to query for news articles.
        Each keyword is separated by a space.

    Returns
    -------
    list of dictionaries
        returns a list of articles, each article is a dictionary with the following structure:
        {
            'source': {
                'id': str,
                'name': str
            },
            'author': str,
            'title': str,
            'description': str,
            'url': str,
            'urlToImage': str,
            'publishedAt': str,
            'content': str
        }
    """

    log_debug("Beginning news request")

    articles = []

    # Make a request for each term
    for term in covid_terms.split(" "):
        # This request returns a json like this:
        # {
        #   'status': str,
        #   'totalResults': number,
        #   'articles': NewsArticle[]
        # }
        request = requests.get("https://newsapi.org/v2/top-headlines", {
            "apiKey": get_config('news_api_key'),
            "q": term.lower(),
            "pageSize": 100,
            "language": "en",
            "page": 1
        })

        # If the status_code isn't one of these, the response might not have a body
        if request.status_code not in [ 200, 426 ]:
            log_info(f"News API request returned status code {request.status_code}")
            continue

        result = request.json()

        if result['status'] == 'error':
            log_info(
                f"News API request returned error code {result['code']} with message:"
                f"{result['message']}"
            )
            continue

        if result['status'] != 'ok':
            log_info(f"News API request returned status {result['status']}")
            continue

        articles += result['articles']

    log_info(f"Finished news request. Found {len(articles)} articles")

    return articles

def update_news() -> None:
    """
    This function replaces news_articles with updated and filtered articles

    It filters based on removed articles' urls.
    """
    global news_articles

    log_info("Performing news update...")

    articles = news_API_request(get_config("search_terms"))

    filtered_articles = []

    for article in articles:
        if article["url"] not in removed_articles:
            filtered_articles.append(article)

    news_articles = filtered_articles

def add_removed_article(article: Dict) -> None:
    """
    This function adds an article to the removed list, preventing it from being
    displayed again.

    Parameters
    ----------
    article : Article
        The article to remove.
        It should contain the following fields
         * url : str
    """
    log_debug(f"Adding removed article {article['url']}")

    # Removed articles are stored by URL since it is the most unique identifier of an article.
    removed_articles.append(article["url"])

def remove_article_by_title(title: str) -> None:
    """
    Removes an article from news_articles by the article's title.
    It will also use add_removed_article to prevent the article from being shown again.

    Parameters
    ----------
    title : str
        The title of the article to remove
    """
    log_debug(f"Removing article with title {title}")
    for article in news_articles:
        if article['title'] == title:
            news_articles.remove(article)
            add_removed_article(article)
            break

def schedule_news_updates(update_interval: float, update_name: str, repeat=False) -> Dict:
    """
    Schedules a news update at the given interval with a given name.

    Parameters
    ----------
    update_interval : number
        The absolute time at which to run the update

    update_name : string
        The name for the update

    repeat : bool
        default -> False
        Whether or not the update should repeat at the given update_interval

    Returns
    -------
    event : Event dictionary
        See scheduler.queue_task
    """

    log_debug(f"Queueing news update {update_news}")

    update_entry = queue_task(update_name, update_news, update_interval, repeat=repeat)

    update_entry['type'] = "News"

    log_info(f"Successfully scheduled news update {update_name}")

    return update_entry
