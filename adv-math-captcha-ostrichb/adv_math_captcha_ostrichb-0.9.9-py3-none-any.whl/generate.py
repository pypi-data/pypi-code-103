import random


def generate_formula(difficulty: int, term: int, number_range: int,
                     factor_range: int = 10,
                     exponentiation_range: int = 50,
                     exp_base_range: int = 6,
                     exp_index_range: int = 5,
                     is_call_inside: bool = False) -> str:
    result_str = ""
    if term <= 0:
        raise SyntaxError("terms cannot be less or equal than zero!")
    if difficulty in [1, 2]:
        # 1 means only contains addition calculation, 2 with subtractions
        element_list = []
        for k in range(term):
            isMinus = False
            if difficulty == 2:
                rand_decision = random.randint(1, 2)
                isMinus = True if rand_decision == 1 else False
            num = random.randint(1, number_range)
            if isMinus:
                num = 0 - num
            element_list.append(num if isMinus else num)
            if num > 0:
                result_str += " + {0}".format(num) if (k != 0 or is_call_inside) else "{0}".format(num)
            else:
                result_str += " - {0}".format(-num) if (k != 0 or is_call_inside) else "{0}".format(num)
    elif difficulty == 3:
        # Multiplication and division included
        for k in range(term):
            if k == 0 and not is_call_inside:
                result_str += "{0}".format(random.randint(-number_range, number_range))
            else:
                control = random.randint(1, 3)
                if control == 1:
                    # Addition and subtraction
                    temp_num = random.randint(-number_range, number_range)
                    if is_call_inside:
                        result_str += " + {0}".format(temp_num) if temp_num >= 0 else " - {0}".format(-temp_num)
                    else:
                        result_str += "+{0}".format(temp_num) if temp_num >= 0 else "{0}".format(temp_num)
                elif control == 2:
                    # Multiplication
                    temp_num = random.randint(-number_range, number_range)
                    result_str += " * {0}".format(temp_num) if temp_num >= 0 else " * ({0})".format(temp_num)
                elif control == 3:
                    # Division, and ensure the result is an integer
                    while 1 == 1:
                        temp_dominator = random.randint(-factor_range, factor_range)
                        if temp_dominator != 0:
                            break
                    temp_numerator = temp_dominator * random.randint(-factor_range, factor_range)
                    numerator_str = "{0}".format(temp_numerator) if temp_numerator >= 0 else \
                        "({0})".format(temp_numerator)
                    dominator_str = "{0}".format(temp_dominator) if temp_dominator >= 0 else \
                        "({0})".format(temp_dominator)
                    result_str += " + {0}/{1}".format(numerator_str, dominator_str)
    elif difficulty == 4:
        # Exponentiation calculation is added
        for k in range(term):
            choice_layer_1 = random.randint(1, 6)
            if choice_layer_1 == 3 and not is_call_inside:
                result_str += generate_formula(3, 1, number_range, factor_range, is_call_inside=True) if k != 0 else \
                    generate_formula(3, 1, number_range, factor_range, is_call_inside=False)
            elif choice_layer_1 in [1, 2] and not is_call_inside:
                result_str += generate_formula(2, 1, number_range, factor_range, is_call_inside=True) if k != 0 else \
                    generate_formula(2, 1, number_range, factor_range, is_call_inside=False)
            elif choice_layer_1 > 3:
                # put an exponentiation as the first element
                temp_base: int = 0
                temp_index: int = 0
                while True:
                    temp_base = random.randint(1, exp_base_range)
                    temp_index = random.randint(1, exp_index_range)
                    if temp_base ** temp_index <= exponentiation_range:
                        break
                result_str += " + ({0}^{1})".format(temp_base, temp_index) if (k != 0 or is_call_inside) else \
                    "({0}^{1})".format(temp_base, temp_index)
    elif difficulty == 5:
        # logarithm will be added this time, enjoy:)
        for k in range(term):
            choice_layer_1 = random.randint(1, 6)
            if choice_layer_1 <= 4:
                result_str += generate_formula(choice_layer_1, 1, number_range, factor_range,
                                               exponentiation_range, exp_base_range, exp_index_range,
                                               is_call_inside=True) if k != 0 else \
                    generate_formula(choice_layer_1, 1, number_range, factor_range,
                                     exponentiation_range, exp_base_range, exp_index_range)
            else:
                # MAKE SURE THAT THERE MUST BE SOME TERRIBLE LOGARITHM ITEMS IN THE FORMULA
                # make a random number here, if one returned, it will be in log(e^x) form
                # (which means ln(e^x) in common sense, as sympy only recognizes the former
                # form, we have to write it like this), if two returned, it will be in log_a (b) form.
                choice_layer_2 = random.randint(1, 2)
                choice_layer_3 = random.randint(1, 2)  # This will determine where it is addition or subtraction
                if choice_layer_2 == 1:
                    if choice_layer_3 == 1:  # addition
                        result_str += " + log(e^{0}, e)".format(random.randint(1, exp_index_range)) if \
                            (k != 0 or is_call_inside) else "log(e^{0}, e)".format(random.randint(1, exp_index_range))
                    else:  # subtraction
                        result_str += " - log(e^{0}, e)".format(random.randint(1, exp_index_range)) if \
                            (k != 0 or is_call_inside) else "-log(e^{0}, e)".format(random.randint(1, exp_index_range))
                else:
                    while True:
                        temp_base = random.randint(2, exp_base_range)
                        temp_index = random.randint(1, exp_index_range)
                        if temp_base ** temp_index <= exponentiation_range:
                            break
                    if choice_layer_3 == 1:  # addition
                        result_str += " + (log({0}, e)/log({1}, e))".format(temp_base ** temp_index, temp_base) if \
                            (k != 0 or is_call_inside) else \
                            "(log({0}, e)/log({1}, e))".format(temp_base ** temp_index, temp_base)
                    else:  # subtraction
                        result_str += " - (log({0}, e)/log({1}, e))".format(temp_base ** temp_index, temp_base) if \
                            (k != 0 or is_call_inside) else \
                            "-(log({0}, e)/log({1}, e))".format(temp_base ** temp_index, temp_base)

    return result_str
