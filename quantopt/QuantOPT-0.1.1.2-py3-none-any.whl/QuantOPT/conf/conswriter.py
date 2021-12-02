# coding=utf-8
from itertools import starmap


class ConsWriter(object):
    @staticmethod
    def _get_kwargs_str(raw_kwargs_str):
        kwargs_list_str = raw_kwargs_str.split('.')
        ori_str = ''
        for i in kwargs_list_str:
            ori_str += (i + '=' + i + ',')
        return ori_str

    @staticmethod
    def func_head(func_name: str, kwargs_str: str, import_func: str):
        head_str = f'def {func_name}({kwargs_str}):'
        if import_func is None:
            import_func = ''
        else:
            import_func = '\t' + ';'.join(import_func) + '\n'
        return head_str + '\n' + import_func

    @staticmethod
    def _sub_head(direction: str, tab: str = '\t'):
        sub_head = tab + f'def func_inner_{direction}(w):'
        return sub_head + '\n'

    @staticmethod
    def _formula(formula, tab: str = '\t'):
        formula_str = tab + tab + 'return ' + formula + '\n'
        return formula_str

    @staticmethod
    def _tail(direction: str, tab: str = '\t'):
        tail_str_4 = tab + f'return func_inner_{direction}'
        return tail_str_4

    @classmethod
    def _writer(cls, func_name: str, kwargs: str, direction: str, formula: str, import_func: str):
        head_str = cls.func_head(func_name, kwargs, import_func)
        sub_head_str = cls._sub_head(direction, )
        formula_str = cls._formula(formula, )
        tail_str = cls._tail(direction)
        deo = head_str + sub_head_str + formula_str + tail_str
        return deo

    @classmethod
    def exec_writer(cls, func_name: str, kwargs: str, direction: str, formula: str, import_func: str):
        exec(cls._writer(func_name, kwargs, direction, formula, import_func))
        return locals()[func_name]

    @classmethod
    def parser(cls, func_name: str, kwargs: str, direction: str, formula: str, import_func: str):
        direction_sample = cls.parser_direction_sample(func_name, direction)
        func_obj = cls.exec_writer(func_name, kwargs, direction_sample, formula, import_func)
        return func_name, func_obj

    @staticmethod
    def parser_direction_sample(func_name, directions: str):
        accept_direct_set = ['eq', 'upper', 'lower']
        if directions in accept_direct_set:
            return directions
        else:
            raise ValueError(
                f"wrong direction value: {directions} for constraints {func_name}, only accept {','.join(accept_direct_set)}")

    @staticmethod
    def load_yaml_settings(f):
        import yaml
        with open(f, 'r+') as conn:
            return yaml.load(conn)

    @classmethod
    def load_all(cls, f):
        y = cls.load_yaml_settings(f)
        for func_name, v in y.items():
            yield func_name, v['kwargs'], v['formula'], v['import_func'], v['direction']

    @classmethod
    def load_parse(cls, f):
        return dict(starmap(cls.parser, cls.load_all(f)))


if __name__ == '__main__':
    pass
