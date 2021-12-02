# coding=utf-8

import yaml

from QuantOPT.conf.conf import setting_yaml_path
from QuantOPT.conf.conswriter import ConsWriter


def main_write(func_name, kwargs, direction, formula, import_func):
    return ConsWriter.exec_writer(func_name, kwargs, direction, formula, import_func)


def parser_direction_sample(func_name, directions):
    if directions in ['eq', 'upper', 'lower']:
        return directions
    else:
        raise ValueError(f"wrong direction value: {directions} for constraints {func_name}, only accept eq,upper,lower")


class Ext(object):
    @staticmethod
    def general_linear_constraint_func(func):
        def general_linear_constraint_func_inner(w):
            return func(w)

        return general_linear_constraint_func_inner


def load_functions(func_name, kwargs, direction, formula, import_func):
    direction_sample = parser_direction_sample(func_name, direction)
    func_obj = main_write(func_name, kwargs, direction_sample, formula, import_func)
    return func_name, func_obj


def set_attribute(cls, func_name, kwargs, direction, formula, import_func):
    # direction_sample = parser_direction_sample(func_name, direction)
    # func_obj = main_write(func_name, kwargs, direction_sample, formula, import_func)
    func_name, func_obj = load_functions(func_name, kwargs, direction, formula, import_func)
    setattr(cls, func_name, func_obj)


def load_yaml_settings(f='./'):
    if isinstance(f, str):
        if f.endswith('.yaml'):
            with open(f, 'r+') as conn:
                return yaml.safe_load(conn)
        else:
            print('try to parse conf text')
            return yaml.safe_load(f)
    elif isinstance(f, dict):
        return f

    else:
        raise ValueError('wrong type of f')


def map_setting_dict(y):
    for func_name, v in y.items():
        yield func_name, v['kwargs'], v['formula'], v['import_func'], v['direction']


def load_all(f='./'):
    return map_setting_dict(load_yaml_settings(f))


class Constraints(Ext):
    pass


# string to attribute
for func_name_sample, kwargs_sample, formula_sample, import_func, direction in load_all(f=setting_yaml_path):
    set_attribute(Constraints, func_name_sample, kwargs_sample, direction, formula_sample, import_func)


def create_constraints_holder(setting_path, cls_name='SpecifiedConstraints'):
    if setting_path is None:
        setting_path = setting_yaml_path
    func_methods = {}
    # string to attribute
    for func_name_sample, kwargs_sample, formula_sample, import_func, direction in load_all(f=setting_path):
        func_name, func_obj = load_functions(func_name_sample, kwargs_sample, direction, formula_sample, import_func)
        func_methods[func_name] = func_obj

    return type(cls_name, (Ext,), func_methods)


if __name__ == '__main__':
    pass
