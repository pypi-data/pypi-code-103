from polidoro_table.string_utils import fill


class Property:
    def __init__(self, size=None, format=None, align=None, method=None, condition=None):
        self.size = size
        self.format = format
        self.align = align
        self.method = method
        self.condition = condition

    @staticmethod
    def apply_properties(value, properties, methods=None):
        from polidoro_table import Format
        globals().update(methods or {})

        format = ''
        align = None
        methods = []
        size = None
        for prop in properties:
            if prop.condition and not eval(prop.condition):
                continue
            format += str(prop.format or '')
            align = prop.align or align
            if prop.method:
                methods.append(prop.method)
            size = prop.size

        value = str(value)
        for m in methods:
            value = m(value)
        return ''.join(format) + fill(value, size, align=align) + str(Format.NORMAL)
