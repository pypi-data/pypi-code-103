import pytest

from .helper import parse_digit, parse_dict, parse_jp

_param_dict_list = [
    {
        "input_param": "1",
        "expected": 1
    }, {
        "input_param": "1.1",
        "expected": 1.1
    }, {
        "input_param": "-1.1",
        "expected": -1.1
    }, {
        "input_param": "-1.10",
        "expected": -1.1
    }, {
        "input_param": "0",
        "expected": 0.0
    }
]

_param_invalid_list = ["a123", "-123a", "123a"]

_dict_to_parse = {
    "data": {
        "records": [{"id": 8}, {"id": 13}, {"id": 99}],
        "detail": {
            "name": "jetty001"
        },
        "new_data": ["5", "ab"],
        "port": ["8080"]
    },
    "code": 909,
    "result": True
}

_dict_to_parse_jp = {
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95,
                "tag": "qa"
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99,
                "tag": "prod"
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99,
                "tag": "qa"
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99,
                "tag": "dev"
            }
        ],
        "bicycle": {
            "color": "red",
            "price": 19.95
        }
    }
}


@pytest.mark.parametrize("dt", _param_dict_list)
def test_parse_digit(dt):
    """
    单元测试： parse digit
    :type dt: dict
    :return:
    """
    expected = dt["expected"]
    actual = parse_digit(dt["input_param"])
    assert expected == actual, \
        "test_parse_digit 失败, input： %r, expected: %r, actual: %r" % (dt["input_param"], expected, actual)


@pytest.mark.parametrize("el", _param_invalid_list)
def test_parse_digit_invalid(el):
    """
    单元测试： parse digit 非法输入
    :param el:
    :return:
    """
    actual = parse_digit(el)
    assert el == actual, \
        "test_parse_digit_invalid 失败, input： %r, expected: %r, actual: %r" % (el, el, actual)


def test_parse_dict_value():
    """
    单元测试，测试解析字典的值
    :return:
    """
    assert parse_dict(dict_data=_dict_to_parse, data_key="data.detail.name") == "jetty001"
    assert parse_dict(dict_data=_dict_to_parse, data_key="data.records[0].id") == 8
    assert parse_dict(dict_data=_dict_to_parse, data_key="data.new_data[1]") == "ab"
    assert parse_dict(dict_data=_dict_to_parse, data_key="code") == 909
    assert parse_dict(dict_data=_dict_to_parse, data_key="data.port[0]") == "8080"


def test_parse_dict_jp():
    """
    单元测试，测试通过 jsonpath 解析字典的值
    :return:
    """
    # assert parse_jp(data_input=_dict_to_parse_jp, jp="$.store.book.[?(@.price > 10)]") == 8.95
    assert parse_jp(data_input=_dict_to_parse_jp, jp="$.store.book.[?(@.tag == 'qa')]") == 8.95
    assert parse_jp(data_input=_dict_to_parse_jp, jp="$.store.book.[?(@.author = 'Nigel Rees')]") == 8.95
    assert parse_jp(data_input=_dict_to_parse_jp, jp="$.store.book[0].price") == 8.95
    assert parse_jp(data_input=_dict_to_parse_jp, jp="$.store.book[0].author") == "Nigel Rees"
