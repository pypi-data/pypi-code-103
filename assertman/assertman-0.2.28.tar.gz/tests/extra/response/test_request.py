import requests
from assertman.objects.assertable_api_response import AssertableResponse
from assertman.matchers import *
import json


def get_data():
    r = requests.post(
        url="https://jsonplaceholder.typicode.com/posts",
        json={
            "name": "John",
            "age": 26,
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
                    "number": "0123-4567-8910",
                    "since": 1993
                },
                {
                    "type": "mobile",
                    "number": "0123-5432-5555",
                    "since": 2011
                }
            ]
        })
    return AssertableResponse(r)


def test_req1():
    r = get_data()
    r.should(has_entries(name="John"))


def test_req_with_extraction():
    r = get_data()
    assert r.extract("name").should(equal_to("John"))
    assert r.should(has_entries(name="John", age=26))
    assert r.extract("phones").should(has_length(3))

    assert r.extract("$.name").should(equal_to("John"))
    assert r.extract("$.phones").should(has_length(3))
    assert r.extract("$.phones[*].type").should(equal_to(["work", "home", "mobile"]))

    assert r.extract("$.phones[*].type") == ["work", "home", "mobile"]

    assert r("phones").should(has_length(3))

    assert r("$.name").should(equal_to("John"))
    assert r("$.phones").should(has_length(3))
    assert r("$.phones[*].type").should(equal_to(["work", "home", "mobile"]))

    assert r("$.phones[*].type") == ["work", "home", "mobile"]
    assert r("$.phones[0].type") == "work"


def test_req_with_filter():
    r = get_data()
    assert r('phones').filter("$[?since > 2000].type").should(equal_to(['work', 'mobile']))
    assert r('phones').filter("$[?since < 2000].type").should(equal_to(['home']))


def test_req_with_find():
    r = get_data()
    assert r('phones').find("$[?since < 2000].type").should(equal_to('home'))


# def test_req_with_wait():
#     r = get_data()
#     r.wait().should(has_entries(name="qwe rty"))






