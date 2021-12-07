import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = {
    "name": "John",
    "age": 26,
    "number": 567,
    "address": {
        "street": "naist street",
        "city": "Nara",
        "postalCode": "630-0192"
    },
    "friends": ["Smith", "Mary", "Kate", "Bob"],
    "phones": [
        {
            "type": "work",
            "number": "0123-4567-8888",
            "since": 2005
        },
        {
            "type": "home",
            "number": "0123-8888-8910",
            "since": 1993
        },
        {
            "type": "mobile",
            "number": "8888-0123-5555",
            "since": 2011
        }
    ]
}


@pytest.mark.parametrize("query, matcher", [
    ('$.name', equal_to("John")),
    ('$.friends', equal_to(['Smith', 'Mary', 'Kate', 'Bob'])),
    ('$.address', has_entries(street="naist street", city="Nara")),
    ('$.address.city', equal_to("Nara"))
])
def test_extract_key(query, matcher):
    """Получение по ключу"""
    assert that(data).extract(query).should(matcher)


@pytest.mark.parametrize("query, matcher", [
    ('$..number', equal_to([567, "0123-4567-8888", "0123-8888-8910", "8888-0123-5555"])),
    ('$..city', equal_to(["Nara"]))
])
def test_recursive_extract_key(query, matcher):
    """Получение рекурсивно по ключу"""
    assert that(data).extract(query).should(matcher)


@pytest.mark.parametrize("query, matcher", [
    ('$.friends[0]', equal_to("Smith")),
    ('$.phones[-1]', has_entries(type="mobile", number="8888-0123-5555")),
    ('$.friends[0:1]', has_length(1)),
    ('$.friends[0:1]', equal_to(["Smith"])),
    ('$.friends[0:2]', has_length(2)),
    ('$.friends[0:2]', equal_to(["Smith", "Mary"])),
    ('$.phones[1:2]', has_length(1)),
    ('$.phones[1:2]', has_item(has_entries(type="home", number="0123-8888-8910"))),
    ('$.phones[1:3]', has_length(2)),
    ('$.phones[1:3]', has_item(has_entries(type="home", number="0123-8888-8910"))),
])
def test_extract_by_index(query, matcher):
    """ Получение из списка по индексу
    * если указан индекс, то возвращается элемент из списка
    * если указан срез, то возвращается список элементов (даже если в срезе всего один элемент)
    """
    assert that(data).extract(query).should(matcher)


@pytest.mark.parametrize("query, matcher", [
    ('$.phones[*].type', equal_to(["work", "home", "mobile"])),
    ('$.phones[0].type', equal_to("work")),
    ('$.phones[0:1].type', equal_to(["work"])),
    ('$.phones[0:2].type', equal_to(["work", "home"])),
])
def test_extract_value_of_key_in_list(query, matcher):
    assert that(data).extract(query).should(matcher)


@pytest.mark.parametrize("query, matcher", [
    ('$.phones[?since > 2000]', [data["phones"][0], data["phones"][2]]),
    ('$.phones[?type = work]', [data["phones"][0]]),
    ('$.phones[?since > 2000 & type = mobile]', [data["phones"][2]]),
    # ('$.phones[?since = 1993 || type = mobile]', [data["phones"][1], data["phones"][2]]),
    # ('$.phones[?number =~ 0123]', [data["phones"][2]]),

    ('$.phones[?since > 2000].number', [data["phones"][0]["number"], data["phones"][2]["number"]]),
    ('$.phones[?type = work].number', [data["phones"][0]["number"]]),
])
def test_extract_with_filters(query, matcher):
    result = that(data).extract(query)
    assert result == matcher







