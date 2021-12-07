import pytest
from assertman.helpers.datetime_helper import DateTimeApi
from assertman.objects.assertable_dict import AssertableDict
from assertman.objects.assertable_list import AssertableList

@pytest.fixture(scope='session')
def doc_json() -> 'AssertableDict':
    return AssertableDict({
        "id": 123456,
        "name": "Твой пакет услуг",
        "is_purchased": True,
        "devices": ["Android Device", "Apple Device", "Stb Device"],
        "stars": None,
        "raitings": {"kinopoisk": 8.9, "imdb": 9.1, "wink": 9.5, },
        "media_items": [
            {"title": "Форсаж",
             "id": 750,
             "is_favorite": True,
             "genres": ["Фантастический фильм", "Дизельный фильм"],
             "assets": {"hd": "https://hd", "sd": "http://sd"}},
            {"title": "Первому игроку приготовиться",
             "id": 1000,
             "is_favorite": True,
             "genres": ["Фантастический фильм", "Фильм по книге"]},
            {"title": "Форест Гамп",
             "id": 50,
             "is_favorite": True,
             "genres": ["Форест, беги", "Спортивный фильм", "Драма"]}
        ],
        "datetimes": {"today": DateTimeApi().today().to_sdp_format(),
                      "today_plus_5_seconds": DateTimeApi().today().customize_date(seconds=5).to_sdp_format(),
                      "today_minus_7_seconds": DateTimeApi().today().customize_date(seconds=-7).to_sdp_format(),
                      "tomorrow": DateTimeApi().tomorrow().to_sdp_format(),
                      "yesterday": DateTimeApi().yesterday().to_sdp_format(),
                      "custom_date": DateTimeApi().today().customize_date(weeks=1, days=2, hours=48).to_sdp_format()}
    })


@pytest.fixture(scope='session')
def doc_list() -> 'AssertableList':

    return AssertableList(
        [
            {"title": "Форсаж",
             "id": 750,
             "is_favorite": True,
             "genres": ["Фантастический фильм", "Дизельный фильм"],
             "assets": {"hd": "https://hd", "sd": "http://sd"}},
            {"title": "Первому игроку приготовиться",
             "id": 1000,
             "is_favorite": True,
             "genres": ["Фантастический фильм", "Фильм по книге"]},
            {"title": "Форест Гамп",
             "id": 50,
             "is_favorite": True,
             "genres": ["Форест, беги", "Спортивный фильм", "Драма"]},
        ],
    )



