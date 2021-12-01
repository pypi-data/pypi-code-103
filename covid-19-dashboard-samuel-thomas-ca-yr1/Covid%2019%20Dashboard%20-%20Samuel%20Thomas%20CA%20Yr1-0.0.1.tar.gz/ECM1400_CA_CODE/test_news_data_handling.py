from news_data_handling import *


def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()


def test_update_news():
    update_news('test')
