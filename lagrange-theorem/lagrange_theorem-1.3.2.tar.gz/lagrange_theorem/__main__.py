"""
This module is the entry point
"""


import argparse
import doctest
import pytest
from input_interval import set_interval
from calculate_numbers import calculate_numbers


def start_program() -> None:
    """
    Function decomposition input numbers and print his
    :return: None
    """
    while (command := input('Enter any symbol to continue '
                            '"stop" ')) != 'stop':
        first_number, second_number = set_interval()
        if first_number is not None and second_number is not None:
            for num, decomp in calculate_numbers(first_number, second_number):
                print(f'{num} -> {decomp}')


def main() -> None:
    """
    Entry point of program
    :return: None
    """
    parser = argparse.ArgumentParser(description='Decomposition numbers')
    parser.add_argument('--mode', type=str, dest='mode', default='input',
                        help='Select mode of working the program')

    args = parser.parse_args()
    if args.mode == 'pytest':
        pytest.main([r"lagrange_theorem\tests\tests.py"])
    elif args.mode == 'doctest':
        doctest.testfile(r'tests/test_calculate_numbers.txt', verbose='-v')
    elif args.mode == 'input':
        start_program()


if __name__ == '__main__':
    main()
