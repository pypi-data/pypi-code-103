"""
Запуск функции, CLI
"""
import sympy
import func
import fire


def main(equation,a,b,accuracy):
    "Запуск функции, обработка результата"
    x = sympy.symbols("x")
    try:
        result = func.newton(x,
                             sympy.sympify(equation),
                             float(a),
                             float(b),
                             float(accuracy))
    except ValueError:
        return None
    if result is None:
        return None
    else:
        return result


if __name__ == '__main__':
    fire.Fire(main)
