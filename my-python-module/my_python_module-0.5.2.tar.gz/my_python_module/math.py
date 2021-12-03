#!/usr/bin/env python
# -*-coding:utf-8-*-

from .exceptions import NotIntegerError, OutOfRangeError


def is_even(n):
    """is this number is even, required input n is a integer.

>>> is_even(0)
True
>>> is_even(-1)
False
>>> is_even(-2)
True

    """
    if not isinstance(n, int):
        raise NotIntegerError

    if n % 2 == 0:
        return True
    else:
        return False


def is_odd(n):
    """is this number is odd, required input n is a integer."""
    return not is_even(n)


def is_prime(n):
    """test input integer n is a prime.
>>> is_prime(0)
False
>>> is_prime(-5)
False
>>> is_prime(-5.2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "__init__.py", line 12, in is_prime
    raise NotIntegerError
my_python_module.exceptions.NotIntegerError
>>> is_prime(5)
True
>>> is_prime(123)
False

    """
    if not isinstance(n, int):
        raise NotIntegerError

    if n == 2:
        return True
    elif n < 2 or not n & 1:
        return False
    for x in range(3, int(n ** 0.5) + 1, 2):
        if n % x == 0:
            return False
    return True


def gen_prime(n):
    """到第n个的所有素数的生成器函数"""
    count = 0
    x = 1
    while count < n:
        if is_prime(x):
            count += 1
            yield x
        x += 1


def gen2_prime(n):
    """到小于某个数n的所有素数的生成器函数"""
    for x in range(n):
        if is_prime(x):
            yield x


def last_gen(genobj):
    """
    迭代一个生成器对象，返回最后一个元素
    :param genobj:
    :return:
    """
    for i in genobj:
        last_e = i

    return last_e


def prime(n):
    """第n个素数 根据last_gen函数，所以integer类型不用判断了
    名字取做prime而不是index_prime是因为计数从1开始。"""
    if n <= 0:
        raise OutOfRangeError("第零个或者第负数个素数？")
    else:
        return last_gen(gen_prime(n))


def gen_fibonacci(n):
    """到第n个的斐波那契数列生成器函数"""
    if not isinstance(n, int):
        raise NotIntegerError

    count = 0
    a, b = 0, 1

    while count < n:
        yield a
        a, b = b, a + b
        count += 1


def fibonacci(n):
    """第几个斐波那契数"""
    if n <= 0:
        raise OutOfRangeError("没有零个或小于零个斐波那契数的概念那。")
    else:
        return last_gen(gen_fibonacci(n))


def gen_factorial(stop, start=1):
    """start*....stop的生成器，默认start=1"""
    if not isinstance(stop, int):
        raise NotIntegerError
    if not isinstance(start, int):
        raise NotIntegerError

    count = 0
    m = start
    n = stop - start + 1
    if stop <= 0:
        raise OutOfRangeError("负数和零的阶乘没有意义")
    elif stop < start:
        raise ValueError("终值应该比初值大")
    else:
        while count < n:
            yield start
            start = start * (m + 1)
            m += 1
            count += 1


def factorial(stop, start=1):
    """start*....stop的值，默认start=1即为stop!的值"""
    if stop <= 0:
        raise OutOfRangeError("负数和零的阶乘没有意义")
    elif stop < start:
        raise ValueError("终值应该比初值大")
    else:
        return last_gen(gen_factorial(stop, start))