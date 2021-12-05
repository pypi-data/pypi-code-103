def get_input() -> tuple[str, str, str]:
    """
    Функция для пользовательского ввода данных, границ и максимального допустимого количества итераций.

    :return: Входные данные для функции
    """
    default_left, default_max_iter = '0', '50'
    left = input('Задайте левую границу диапазано (пустая строка для значения по умолчанию = 0): ')
    right = input('Введите правую границу диапазона (обязательно): ')
    max_iter = input('Введите максимальное число чисел (пустая строка для значения по умолчанию = 50): ')
    if not left:
        left = default_left
    if not max_iter:
        max_iter = default_max_iter
    if left.isnumeric() and right.isnumeric() and max_iter.isnumeric():
        return left, right, max_iter
    return '', '', ''
