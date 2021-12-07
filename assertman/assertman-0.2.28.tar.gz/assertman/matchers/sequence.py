from functools import cmp_to_key

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher


contains = hamcrest.contains
contains_inanyorder = hamcrest.contains_inanyorder
has_item = hamcrest.has_item
has_items = hamcrest.has_items
is_in = hamcrest.is_in
# only_contains = hamcrest.only_contains
empty = hamcrest.empty


class HasItemAtIndex(BaseMatcher):
    """ Матчер проверки того что элемент с заданным индексом удовлетворяет условию"""

    def __init__(self, index, matcher):
        self.index = index
        self.matcher = matcher
        self.error = None

    def _matches(self, item):
        if not isinstance(item, list) or not item:
            return False
        try:
            return self.matcher.matches(item[self.index])
        except IndexError as error:
            self.error = error
            return False

    def describe_to(self, description):
        description.append_text(
            f"a sequence containing at index"
            f" {self.index} element ").append_description_of(self.matcher)

    def describe_mismatch(self, item, mismatch_description):
        if self.error:
            mismatch_description.append_text(
                f"failed get item by index {self.index} from sequence"
                f" {item} because: '{self.error}'")
        else:
            mismatch_description.append_text(f"was {item[self.index]}")


def has_item_at_index(index, matcher):
    """ Проверить, что в списке элемент с переданным индексом удовлетворяет переданному матчеру
    :param index: индекс
    :param matcher: объект типа матчер (см. примеры)

    Examples:
        list = ["one", "two", "three"]
        assert_that(list, has_item_at_index(2, equal_to("three")))

        list = [{"currency": "BTC"}, {"currency": "USD"}, {"currency": "RUB"}]
        assert_that(list, has_item_at_index(0, has_value("BTC")))
    """
    return HasItemAtIndex(index, wrap_matcher(matcher))


def has_first_item(matcher):
    """ Проверить, что в списке  первый элемент  удовлетворяет переданному матчеру
    :param matcher: объект типа матчер (см. примеры)

    Examples:
        list = ["one", "two", "three"]
        assert_that(list, has_first_item(equal_to("one")))
    """
    return HasItemAtIndex(0, wrap_matcher(matcher))


def has_last_item(matcher):
    """ Проверить, что в списке  последний элемент  удовлетворяет переданному матчеру
    :param matcher: объект типа матчер (см. примеры)

    Examples:
        list = ["one", "two", "three"]
        assert_that(list, has_last_item(equal_to("three")))
    """
    return HasItemAtIndex(-1, wrap_matcher(matcher))


class HasUniqueItems(BaseMatcher):
    """ Матчер проверки того что cписок имеет только уникальные элементы"""

    def _matches(self, item):
        if not isinstance(item, list) or not item:
            return False
        return len(item) == len(set(item))

    def describe_to(self, description):
        description.append_text('a sequence has only unique items')


def has_unique_items():
    """ Проверить, что список не содержит повторяющихся элементов

    Examples:
        list = ["one", "two", "three"]
        assert_that(list, has_unique_items())
    """
    return HasUniqueItems()


class EveryItem(BaseMatcher):
    """ Матчер проверки того, что каждый элемент списка соответствует переданному матчеру """

    def __init__(self, matcher):
        self.matcher = matcher
        self.unmatched_items = []

    def _matches(self, item):
        if not isinstance(item, list) or not item:
            return False
        for i in item:
            if not self.matcher.matches(i):
                self.unmatched_items.append(i)
        return len(self.unmatched_items) == 0

    def describe_to(self, description):
        description.append_text('every item in a sequence ') \
            .append_description_of(self.matcher)

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text(
            f"found {len(self.unmatched_items)} unmatched items:"
            f" {self.unmatched_items}\n in {item}")


def every_item(matcher):
    """ Проверить, что каждый элемент списка удовлетворяет переданному матчеру
    Иногда бывает удобнее использовать этот матчер, вместо цикла "for", а иногда наоборот
    - он все только усложняет
    :param matcher: объект типа матчер (см. примеры)

    Examples:
        list = [{"price": 300}, {"price": 890}, {"price": 111}]
        assert_that(list, every_item(has_entry("price", greater_than(100))))
    """
    return EveryItem(matcher)


class HasListOrdered(BaseMatcher):
    """ Матчер проверки упорядоченности списка"""

    def __init__(self, reverse, compare):
        self.reverse = reverse
        self.compare = compare

    def _matches(self, item):
        if not isinstance(item, list) or not item:
            return False
        if self.compare:
            return item == sorted(item, reverse=self.reverse, key=cmp_to_key(self.compare))
        return item == sorted(item, reverse=self.reverse)

    def describe_to(self, description):
        description.append_text('a sequence has ordered in {} order'.format(
            'descendant' if self.reverse else 'ascendant'))


def has_list_ordered(reverse=False, compare=None):
    """ Проверить, что список отсортирован
    :param reverse: Если True - в обратном порядке
    :param compare: Кастомная функция сравнения элементов
    Examples:
        list = ["1", "2", "3"]
        assert_that(list, has_list_ordered()))
    """
    return HasListOrdered(reverse, compare)


class AllSame(BaseMatcher):
    """ Матчер проверки что список состоит из одинаковых значений"""

    def _matches(self, item):
        if not isinstance(item, list) or not item:
            return False
        return len(set(item)) == 1

    def describe_to(self, description):
        description.append_text('all items in list same')


def all_same():
    """ Проверить, что в списке только одинаковые значения

    Examples:
        list = ["1", "1", "1"]
        assert_that(list, all_same()))
    """
    return AllSame()
