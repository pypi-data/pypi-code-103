import argparse
import pytest

import dijkstra_alg
from .dijkstra import dijkstra
from .is_valid_input import is_valid



def main():
    parser = argparse.ArgumentParser(description='Кратчайший путь между '
                                                 'узлами графа по алгоритму дейкстры')
    parser.add_argument('-v', '--variant', dest='variant', default='gui',
                        help='Вариант работы программы, '
                             'где gui - запуск программы, pytest - '
                             'Вывод результатов тестов pytest')
    args = parser.parse_args()
    if args.variant == 'pytest':
        pytest.main([dijkstra_alg.__path__[0] + r"\tests\test_dijkstra.py"])
    elif args.variant == 'gui':
        while (
                info := input(
                    'Введите имя файла с матрицей, начальный '
                    'и конечный узел или "end" для выхода:\n')) != 'end':
            try:
                if res := is_valid(info):
                    print(dijkstra(*res))
                else:
                    print('Некорректный ввод')
            except ValueError as e:
                print(f'Ошибка в введенных данных: {e}')


if __name__ == '__main__':
    main()
