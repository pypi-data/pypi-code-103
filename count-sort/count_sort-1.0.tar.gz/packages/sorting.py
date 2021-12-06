"""
Модуль для сортировки чисел методом подсчета

Шестера Дмитрий
typa_lya@mail.ru

Используется для сортировки чисел на основании данных,
полученних в модуле input_data(числа)

Ф-я count_sort - сортировка чисел методом подсчета
"""


def count_sort(numbers_mas: list) -> list:
    """
    Функция для сортировки чиселом методом подсчета
    :param numbers_mas: список чисел, которые нужно отсортировать
    :return: list, отсортированный список чисел
    >>> count_sort([345, -4, 45, -4, 0])
    [-4, -4, 0, 45, 345]
    >>> count_sort([-324, -4, -54, 0, -345])
    [-345, -324, -54, -4, 0]
    """
    count_mas = []
    last = max(numbers_mas) + 1
    first = min(numbers_mas)
    if first <= 0 <= last:
        count_mas = [0] * (last - first + 1)
    elif (last >= 0) and (first >= 0):
        count_mas = [0] * last
    elif last <= 0 and first <= 0:
        count_mas = [0] * (-first + 1)
    for i in numbers_mas:
        count_mas[i] += 1
    numbers_mas = []
    for k in range(first, last):
        numbers_mas += [k] * count_mas[k]
    return numbers_mas
