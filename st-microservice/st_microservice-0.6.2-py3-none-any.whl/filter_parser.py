from typing import Callable
import pyparsing as pp


date_exp = pp.Opt(pp.one_of('< <= > >= <> != ='), '=') + pp.common.iso8601_date


def number_filter_parser(query, field, filter_string: str) -> Callable[[str], bool]:
    exp = pp.Opt(pp.one_of('< <= > >= <> != ='), '=') + pp.common.number + pp.LineEnd()
    tokens = exp.parse_string(filter_string)
    operator = tokens[0]

    q = query
    f = field
    v = tokens[1]
    return {
        '=': q.where(f == v),
        '<': q.where(f < v),
        '<=': q.where(f <= v),
        '>': q.where(f > v),
        '>=': q.where(f >= v),
        '<>': q.where(f != v),
        '!=': q.where(f != v)
    }[operator]


def boolean_filter_parser(query, field, filter_string: str) -> Callable[[str], bool]:
    exp = pp.one_of(['y', 'yes', 'true', 'n', 'no', 'false'], True) + pp.LineEnd()
    token = exp.parse_string(filter_string)[0]

    if token in ['y', 'yes', 'true']:
        return query.where(field == True)
    else:
        return query.where(field == False)
