"""test_covid_news_handler module

This module exports functions intended to test the functionality of the
covid_news_handler module.

The following functions are not testable for various reasons:
 - news_API_request
 - update_news
 - schedule_news_updates
 - remove_article_by_title
"""

import covid19dashboard.covid_news_handler as covid_news_handler

def reset_test_environment():
    """
    This function resets the test environment by resetting default values.
    """
    covid_news_handler.news_articles = []
    covid_news_handler.removed_articles = []

def test_add_removed_article():
    """
    This test ensures that add_removed_article adds an article's url to the removed list
    """
    reset_test_environment()

    test_url = "https://www.google.com"
    test_article = {
        "url": test_url
    }

    covid_news_handler.add_removed_article(test_article)

    assert covid_news_handler.removed_articles == [ test_url ]
