# -*- coding:utf-8 -*-

class API(object):
    def __init__(self, infos: dict, calls: dict,
                 security: dict, servers: dict):
        self.infos = infos
        self.calls = calls
        self.security = security
        self.servers = servers
    
    def get_calls(self):
        return [k for k,_ in self.calls.items()]


class Call(object):
    def __init__(self, name: str, input_fields: dict, output_fields: dict,
                 required: list, tag: str, unauthenticated: bool,
                 description: str = 'TODO_REQ_DESC',
                 description_response: str = 'TODO_RESP_DESC',
                 http_verb: str = 'post') :
        self.name = name
        self.input_fields = input_fields
        self.output_fields = output_fields
        self.required = required
        self.tag = tag
        self.unauthenticated = unauthenticated
        self.description = description
        self.description_response = description_response
        self.http_verb = http_verb

    def __eq__(self, other):
        return ((self.name, self.input_fields, self.input_fields, self.required, self.tag)
                == (other.name, other.input_fields, other.input_fields, other.required, other.tag))

    def __ne__(self, other):
        return not(self == other)

    def merge(self, other):
        self.dict_merge(self.input_fields, other.input_fields)
        self.dict_merge(self.output_fields, other.output_fields)
        for x in other.required:
            if x not in self.required:
                self.required.append(x)

    def dict_merge(self, fields: dict, other_fields):
        for k, v in other_fields.items():
            if k not in fields:
                fields[k] = v
                continue
            if isinstance(v, ArrayField) or isinstance(v, ObjectField):
                fields[k].__add__(v)
            #else:
            #    print('same field ;) {} {}'.format(k, v))


class Field(object):
    def __init__(self, name: str, type: str, way: str, call_name: str):
        self.name = name
        self.type = type
        self.flag_uniq_by_call = False
        self.flag_uniq_by_way = False
        self.way = way
        self.call_name = call_name
        self.path_key = None

    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        return (self.name, self.type) == (other.name, other.type)

    def __ne__(self, other):
        return not(self == other)


class ObjectField(Field):
    def __init__(self, properties: dict, *args, description=None):
        super().__init__(*args)
        self.properties = properties
        self.description = description

    def __hash__(self):
        return hash((
            super().__hash__(),
            tuple([hash(x) for x in self.properties.values()])
        ))

    def __eq__(self, other):
        return (super().__eq__(other)
                and self.properties == other.properties)

    def __add__(self, other):
        for k, v in other.properties.items():
            if k not in self.properties:
                self.properties[k] = v
                continue
            if isinstance(v, ArrayField) or isinstance(v, ObjectField):
                self.properties[k].__add__(v)
            #else:
            #    print('same field ;) {} {}'.format(k, v))


class ArrayField(Field):
    def __init__(self, item, *args, description=None):
        super().__init__(*args)
        self.item = item
        self.description = description

    def __hash__(self):
        return hash((super().__hash__(), self.item))

    def __eq__(self, other):
        return (super().__eq__(other) and self.item == other.item)

    def __add__(self, other):
        if type(other.item) is ObjectField:
            for k, v in other.item.properties.items():
                if k not in self.item.properties:
                    self.item.properties[k] = v
                    continue
                if isinstance(v, ArrayField) or isinstance(v, ObjectField):
                    self.item.properties[k].__add__(v)
                #else:
                #    print('same field ;) {} {}'.format(k, v))


class TerminalField(Field):
    def __init__(self, *args, default=None, fieldformat=None, required=False, description=None):
        super().__init__(*args)
        self.required = required
        self.format = fieldformat
        self.default = default
        self.description = description

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()
