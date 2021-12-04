#!/usr/bin/env python3
from utils import timeit

@timeit
def main(x: int, y, z) -> int:
    result = x ** 2
    print(f'The answer is {result}')
    return result

if __name__ == '__main__':
    result, runtime = main(1000, 1, 1)
