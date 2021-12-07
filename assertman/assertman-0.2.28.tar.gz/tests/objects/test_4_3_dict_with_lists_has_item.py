import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = {
    "cities": [
        {"name": "Moscow", "year": 1147, "is_capital": True},
        {"name": "London", "year": 47, "is_capital": True},
        {"name": "NewYork", "year": 1603, "is_capital": True}
    ],
}


# ------- has_item

def test_has_item():
    """Позитивный тест"""
    assert that(data).should(has_entries(
        cities=has_item({"name": "London", "year": 47, "is_capital": True})
    ))


def test_raises_has_item():
    """Срабатывание ассерта в позитивном тесте"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=has_item({"name": "Paris", "year": 47, "is_capital": True})
        ))


@pytest.mark.skip
def test_not_has_item():
    """Тест с отрицанием"""
    assert that(data).should(has_entries(
        cities=not_(has_item({"name": "Paris", "year": 47, "is_capital": True}))
    ))


@pytest.mark.skip
def test_raises_not_has_item():
    """Срабатывание ассерта в тесте с отрицанием"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=not_(has_item({"name": "London", "year": 47, "is_capital": True}))
        ))


# ------- has_items

def test_has_items():
    """Позитивный тест (обе записи есть в списке)"""
    assert that(data).should(has_entries(
        cities=has_items(
            {"name": "London", "year": 47, "is_capital": True},
            {"name": "Moscow", "year": 1147, "is_capital": True}
        )))


@pytest.mark.parametrize("matcher", [
    # обе записи отсутствуют в спискке
    has_items(
        {"name": "Paris", "year": 47, "is_capital": True},
        {"name": "Tokio", "year": 1147, "is_capital": True}
    ),
    # только первая запись отсутствует в списке
    has_items(
        {"name": "Paris", "year": 47, "is_capital": True},
        {"name": "Moscow", "year": 1147, "is_capital": True}
    ),
    # только вторая запись отсутствует в списке
    has_items(
        {"name": "London", "year": 47, "is_capital": True},
        {"name": "Tokio", "year": 1147, "is_capital": True}
    ),
])
def test_raises_has_items(matcher):
    """Срабатывание ассерта в позитивном тесте"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=matcher
        ))


@pytest.mark.skip
def test_not_has_items():
    """Тест с отрицанием (обе записи отсутствуют в списке)"""
    assert that(data).should(has_entries(
        cities=not_(has_items(
            {"name": "Rim", "year": 47, "is_capital": True},
            {"name": "Tokio", "year": 1147, "is_capital": True}
        ))))


@pytest.mark.skip
@pytest.mark.parametrize("matcher", [
    # обе записи присутствуют в спискке
    has_items(
        {"name": "London", "year": 47, "is_capital": True},
        {"name": "Moscow", "year": 1147, "is_capital": True}
    ),
    # только первая запись присутствует в списке
    has_items(
        {"name": "London", "year": 47, "is_capital": True},
        {"name": "Tokio", "year": 1147, "is_capital": True}
    ),
    # только вторая запись присутствует в списке
    has_items(
        {"name": "Tokio", "year": 47, "is_capital": True},
        {"name": "Moscow", "year": 1147, "is_capital": True}
    ),
])
def test_raises_not_has_items(matcher):
    """Срабатывание ассерта в тесте с отрицанием"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=has_items(
                {"name": "London", "year": 47, "is_capital": True},
                {"name": "Moscow", "year": 1147, "is_capital": True}
            )))


# ------- has_item has_entries

@pytest.mark.parametrize("matcher", [
    # тест с матчингом по части слоаря
    has_item(has_entries(name="Moscow")),
    # тест с матчингом по полному словарю
    has_item(has_entries(name="NewYork", year=1603, is_capital=True)),
])
def test_has_item_has_entries(matcher):
    """Позитивный тест"""
    assert that(data).should(has_entries(
        cities=matcher))

@pytest.mark.parametrize("matcher", [
    # тест с матчингом по части слоаря
    has_item(has_entries(name="Tokio")),
    # тест с матчингом по полному словарю
    has_item(has_entries(name="Tokio", year=1603, is_capital=True)),
])
def test_raises_has_item_has_entries(matcher):
    """Срабатывание ассерта в позитивном тесте"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=matcher))


@pytest.mark.skip
@pytest.mark.parametrize("matcher", [
    # тест с отрицанием по части слоаря
    not_(has_item(has_entries(name="Tokio"))),
    # тест с отрицанием по полному словарю
    not_(has_item(has_entries(name="Tokio", year=1603, is_capital=True))),
])
def test_not_has_item_has_entries(matcher):
    """Тест с отрицанием"""
    assert that(data).should(has_entries(
        cities=matcher))


@pytest.mark.skip
@pytest.mark.parametrize("matcher", [
    # тест с матчингом по части слоаря
    not_(has_item(has_entries(name="Moscow"))),
    # тест с матчингом по полному словарю
    not_(has_item(has_entries(name="NewYork", year=1603, is_capital=True))),
])
def test_raises_not_has_item_has_entries(matcher):
    """Срабатывание ассерта в тесте с отрицанием"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=matcher))

#
# # ------- has_items has_entries
#
# def test_has_items_has_entries1():
#     assert that(data).should(has_entries(
#         cities=has_items(
#             has_entries(name="Moscow"),
#             has_entries(name="NewYork")
#         )))
#
#
# def test_has_items_has_entries2():
#     assert that(data).should(has_entries(
#         cities=has_items(
#             has_entries(name="NewYork", year=1603),
#             has_entries(name="Moscow", year=1147)
#         )))
#
#
# def test_not_has_items_has_entries():
#     assert that(data).should(has_entries(
#         cities=has_items(
#             has_entries(name="NewYork", year=1603),
#             has_entries(name="Paris", year=1147)
#         )))
#
#
# def test_raises_has_items_has_entries():
#     with pytest.raises(AssertionError) as excinfo:
#         assert that(data).should(has_entries(
#             cities=has_items(has_entries(
#                 name="Moscow",
#                 year=22
#             ))))
#
#
# def test_raises_not_has_items_has_entries():
#     with pytest.raises(AssertionError) as excinfo:
#         assert that(data).should(has_entries(
#             cities=not_(has_items(has_entries(
#                 name="NewYork",
#                 year=1604
#             )))))