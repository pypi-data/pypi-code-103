"""
Основной модуль пакета, выступакет в роли точки входа


Ф-я reenter - повторный ввод с возможностью завершения
Ф-я main - командный линейный интерфейс (выбор режима запуска)
"""
import click
from sorting import count_sort
from data_input import data_input
import pytest
import doctest


def reenter():
    """
    Функция повторного ввода или завершения
    """
    while (s := input('Для завершения введите stop: ')) != 'stop':
        data = data_input()
        mas = count_sort(data)
        print(*mas)


@click.command()
@click.option(
    "--mode", "-m", help="Выберите режим работы: "
                         "pytest - вывод тестов pytest; "
                         "doctest - вывод тестов doctest; "
                         "start - запуск программы")
def main(mode: str):
    """
    Реализация командного линейного интерфейса

    :param mode: режим работы пакета
    :type mode: str
    """
    if mode == "pytest":
        pytest.main(['-v'])
    elif mode == "doctest":
        doctest.testmod()
    elif mode == "start":
        reenter()


if __name__ == '__main__':
    main()
