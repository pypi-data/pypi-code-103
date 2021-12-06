"""
Пример работы функции метода Ньютона
"""
import sympy
import __main__

def example_1():
    """Ввод:x**3-27*x
            0
            4
            0.00001"""
    return __main__.main(sympy.sympify("x**3-27*x"),
                         0,
                         4,
                         0.00001)
    #3,-54

def example_2():    
    """Ввод:x**3-3*x**2+2
            1
            4
            0.00001"""
    return __main__.main(sympy.sympify("x**3-3*x**2+2"),
                         1,
                         4,
                         0.0001)
    #2,-2

def example_3():
    """Ввод:x**3-2*x**2+x+3
            1
            4
            0.0001"""
    return __main__.main(sympy.sympify("x**3-2*x**2+x+3"),
                         1,
                         4,
                         0.0001)
    #1,3

def example_4():
    """Ввод:x**3-2*x**2+x+3
            1
            4
            0.0001"""
    return __main__.main(sympy.sympify("x**3-2*x**2+x+3"),
                         5,
                         4,
                         0.0001)
    #None

def example_5():
    """Ввод:asd
            df
            asd
            asds"""
    return __main__.main("asd",
                         "df",
                         "asd",
                         "asds")
    #None
