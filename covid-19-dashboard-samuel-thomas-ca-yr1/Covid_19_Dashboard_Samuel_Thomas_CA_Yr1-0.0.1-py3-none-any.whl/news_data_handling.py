"""[This is module that handles the collection and processing of a news API]

"""
import sched
import time
from newsapi import NewsApiClient
from config import headlines, schedule_update_remove, key
from handlers_logging import logger_news_handler

# news scheduler
scheduler_news = sched.scheduler(time.time, time.sleep)


def update_news_event(update_name: str) -> None:
    """[A function to start the process to remove a schedule from the config file]

    Args:
        update_name (str): [the schedules title]
    """
    global ARTICLES
    ARTICLES = news_API_request()  # update the articles global variable
    # remove the now schedule from the schedule list
    schedule_update_remove(update_name)
    logger_news_handler.info('ARTCILES uopdated')
    logger_news_handler.info('removed from scheduler_news')


def update_news(update_name: str, update_interval: int = 10) -> None:
    """[A function that creates a schedule to update the news API]

    Args:
        update_name (str): [the schedules title]
        update_interval (int, optional): [the schedules time delay. Defaults to 10.]
    """
    scheduler_news.enter(update_interval, 1, update_news_event, kwargs={
        'update_name': update_name})  # add the schedule to the news scheduler
    logger_news_handler.info('schedule added to scheduler_news')


def process_news_api(articles_current: dict) -> dict:
    """[A function to remove unwanted news from the news collected by the API]

    Args:
        articles_current (dict): [the API collected news]

    Returns:
        dict: [the filtered news articles]
    """
    global ARTICLES
    i = 0
    for news in articles_current:
        for j in range(0, len(headlines)):
            if news['title'] == headlines[j]:
                # adding the full data to the config file headlines
                headlines[j] = news
        i += 1
    # removing the unwanted news from the API data
    ARTICLES = [x for x in articles_current if x not in headlines]
    logger_news_handler.info('Articles have been filtered and processed')
    return ARTICLES  # return the processed API data


def news_API_request(covid_terms: str = 'Covid COVID-19 coronavirus') -> dict:
    """[A function that collects news using a news API]

    Args:
        covid_terms (str, optional): [terms to filter by. Defaults to 'Covid COVID-19 coronavirus'.]

    Returns:
        dict: [the API collected data]
    """
    newsapi = NewsApiClient(api_key=key)
    # collecting the news API data
    covid_articles = newsapi.get_everything(q=covid_terms,
                                            sources='bbc-news',
                                            domains='bbc.co.uk',
                                            language='en',
                                            sort_by='relevancy',
                                            page=2)
    logger_news_handler.info('News API collected and processed')
    # returing the processed news API data
    return process_news_api(covid_articles['articles'])


# assign my global variables the news API requests
ARTICLES = news_API_request()
