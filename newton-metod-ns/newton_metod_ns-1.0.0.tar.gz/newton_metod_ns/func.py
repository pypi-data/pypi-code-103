import sympy


def newton(x,f,a,b,accuracy):
    """Нахождение минимума функции по методу Ньютона"""
    f1 = f.diff(x)
    f2 = f1.diff(x)
    xn = (a + b) / 2
    xn1 = xn - (f1.subs(x, xn) / f2.subs(x, xn))
    if not (isinstance(xn1, sympy.core.numbers.Float) or xn1 == 0) or (
    xn1 > b or xn1 < a):
        return None
    while abs(xn1 - xn) > accuracy:
        xn = xn1
        xn1 = xn - (f1.subs(x, xn) / f2.subs(x, xn))
        if not (isinstance(xn1, sympy.core.numbers.Float) or xn1 == 0) or (
        xn1 > b or xn1 < a):
            return None
    xn1 = round(xn1, len(str(accuracy))-2)
    if f1.subs(x, xn1) == 0 and f2.subs(x, xn1) > 0:
        return xn1, f.subs(x, xn1)
    return None
