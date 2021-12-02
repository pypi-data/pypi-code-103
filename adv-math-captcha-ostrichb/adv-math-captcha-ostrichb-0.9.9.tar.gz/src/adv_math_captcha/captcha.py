from .generate import generate_formula
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
import math


class Captcha:
    def __init__(self, difficulty: int, term: int, number_range: int,
                 factor_range: int = 10,
                 exponentiation_range: int = 50,
                 exp_base_range: int = 6,
                 exp_index_range: int = 5):
        self.formula_str = generate_formula(difficulty, term, number_range, factor_range,
                                            exponentiation_range, exp_base_range, exp_index_range)
        self.__formula_obj = parse_expr(self.formula_str.replace("^", "**").replace("e", "E"))
        self.evaluation = N(self.__formula_obj, 5)
        # change the string's appearance after evaluated
        self.formula_str = self.formula_str.replace(', e)', ')')
        self.formula_str = self.formula_str.replace('log(', 'ln(')

    def verify(self, user_input: float) -> bool:
        if math.fabs(self.evaluation - user_input) <= 10 ** -4:
            # Because of the lack of computer, an error range is given instead of simple equality check.
            return True
        else:
            return False


if __name__ == '__main__':
    formula1 = Captcha(5, 4, 15, 10, 50, 5, 5)
    inp = input("Solve this simple question: {0} = ".format(formula1.formula_str))
    if formula1.verify(float(inp)):
        print("Verify success!")
    else:
        print("Verify failed! The correct answer is {0:.0f}!".format(float(formula1.evaluation)))