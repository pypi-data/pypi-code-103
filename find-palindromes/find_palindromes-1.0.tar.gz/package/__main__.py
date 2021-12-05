"""
Основной модуль пакета, выступающий в роли точки входа


Функция reenter - повторный ввод с возможностью завершения,
и вывода соответствующей информации в случае некоректного ввода
Функция main - Реализация интерфейса командной строки (выбор режима запуска)
"""

import click
import pytest
import doctest
import palindromes
from palindromes import find_palindromes
from input_getter import get_input


def start():
    """
    Функция для повторного запуска или вывода информации об ошибках
    """
    while (_ := input('Для продолжения нажмите Enter, для завершения введите "quit": ')) != "quit":
        params = get_input()
        if any(params):
            left_border, right_border, number_of_iterations = map(int, params)
            print(*palindromes.find_palindromes(left_border, right_border, number_of_iterations), sep='\n')
        else:
            print('Некоректный ввод. Попробуйте еще раз.\n')


@click.command()
@click.option("--mode", "-m",
              type=click.Choice(["start", "pytest", "doctest"], case_sensitive=True),
              help="Выберите режим работы: start - запуск программы; "
                   "pytest - вывод тестов pytest; doctest - вывод тестов doctest.")
def main(mode: str):
    """
    Реализация интерфейса командной строки

    :param mode: режим запуска пакета
    :type mode: str
    """
    if mode == 'start':
        start()
    elif mode == 'pytest':
        pytest.main(['-v'])
    elif mode == 'doctest':
        doctest.testmod(palindromes, verbose=True)


if __name__ == '__main__':
    main()
