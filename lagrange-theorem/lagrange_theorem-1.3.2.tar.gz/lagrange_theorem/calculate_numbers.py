"""
Module decomposition numbers of theorem of Lagrange
"""


def lagrange(num: int) -> tuple:
    """
    Function of decomposition numbers into sum of four squares
    :param num: Input number
    :return: Tuple of decomposition number
    """
    maximum = int(num ** 0.5)
    for i in range(maximum + 1):
        for j in range(maximum + 1):
            for k in range(maximum + 1):
                for l in range(maximum + 1):
                    if i ** 2 + j ** 2 + k ** 2 + l ** 2 == num:
                        return l, k, j, i


def calculate_numbers(left_border: int, right_border: int) -> list:
    """
    Function decompose number in interval [a, b)
    :param left_border: First number in interval
    :param right_border: Last number in interval (do not enter)
    :return:
    """
    list_of_numbers = []
    for i in range(left_border, right_border):
        list_of_numbers.append(
            tuple([i, lagrange(i)]))

    return list_of_numbers
