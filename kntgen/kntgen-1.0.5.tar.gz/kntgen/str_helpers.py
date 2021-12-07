# coding=utf-8
import re
import time


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


def create_file_name(class_name) -> str:
    if is_camel_case(class_name):
        upper_case_letters = re.findall('[A-Z][^A-Z]*', class_name)
        return '_'.join(upper_case_letters).lower()
    else:
        print(
            'Invalid filename. Filename need to be camel string.\nFor '
            'example: MyCamelCase')
        exit(1)


def is_camel_case(st) -> str:
    return st != st.lower() and st != st.upper() and "_" not in st


def lower_first_letter(st) -> str:
    return st[0].lower() + st[1:]


def upper_first_letter(st) -> str:
    return st[0].upper() + st[1:]


def snake_to_camel(st) -> str:
    components = st.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def snake_to_pascal(st) -> str:
    components = st.split('_')
    return ''.join(x.title() for x in components)


def to_words(st) -> str:
    return ' '.join(to_snake_case(st).split('_')).lstrip()


def to_snake_case(st) -> str:
    result = []
    for i in range(len(st)):
        char = st[i]
        if char == ' ' or char == '_':
            if (i < len(st) - 1) and (st[i + 1] == '_'
                                      or st[i + 1] == ' '
                                      or st[i + 1].isupper()):
                continue
            result.append('_')
        elif char.isupper():
            result.append(f'{"_" if i > 0 else ""}{char.lower()}')
        else:
            result.append(char)
    return ''.join([c for c in result])


def to_camel_case(st) -> str:
    return snake_to_camel(to_snake_case(st))


def to_pascal_case(st) -> str:
    return snake_to_pascal(to_snake_case(st))


def plural_to_singular(st) -> str:
    if st.endswith('ies'):
        if len(st) > 3:
            if st[-4] not in 'aeiou':
                return st[0:-3] + 'y'
    elif st.endswith('es'):
        if st[-3] in 'sxo':
            return st[0:-2]
        elif st[-4:-2] == 'ch' or st[-4:-2] == 'sh':
            return st[0:-2]
        else:
            return st[0:-1]
    elif st.endswith('s'):
        if len(st) > 3:
            return st[:-1]
    return st


def is_number(st) -> bool:
    try:
        float(st)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(st)
        return True
    except (TypeError, ValueError):
        pass

    return False


def is_time_format(st):
    try:
        time.strptime(st, '%H:%M')
        return True
    except ValueError:
        return False
