def find_palindromes(left_border: int, right_border: int, number_of_iterations: int = 50) -> list[tuple[int, int, int]]:
    """
    Функция для нахождения палиндромов в заданном диапазоне,
    путем применения операций "перевернуть и сложить"

    :param right_border: Правая граница диапазона
    :type right_border: int
    :param left_border: Левая граница диапазона (по умолчанию не задана, т.е. 0)
    :type left_border: int
    :param number_of_iterations: Максимально допустимое количество итераций (по умолчанию 50)
    :type number_of_iterations: int
    :return: Список кортежей из троек чисел, найденных палиндромов, где
             1-ый элемент - число, из которого был получен палиндром
             2-ой элемент - полученный палиндром
             3-ий элемент - потребовашееся количество итераций

    >>> find_palindromes(0, 5)
    [(0, 0, 0), (1, 1, 0), (2, 2, 0), (3, 3, 0), (4, 4, 0)]
    >>> find_palindromes(87, 92, 3)
    [(88, 88, 0), (90, 99, 1), (91, 121, 2)]
    """
    palindromes = []
    for i in range(left_border, right_border):
        iteration_counter = 0
        result = i
        while str(result) != str(result)[::-1] and iteration_counter < number_of_iterations:
            result += int(str(result)[::-1])
            iteration_counter += 1
        if str(result) == str(result)[::-1]:
            result_tuple = (i, result, iteration_counter)
            palindromes.append(result_tuple)
    return palindromes
