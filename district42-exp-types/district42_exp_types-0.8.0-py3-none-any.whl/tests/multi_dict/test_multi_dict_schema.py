from baby_steps import given, then, when
from district42 import schema
from district42.errors import DeclarationError
from multidict import MultiDict, MultiDictProxy
from pytest import raises

from district42_exp_types.multi_dict import MultiDictSchema, schema_multi_dict


def test_multi_dict_declaration():
    with when:
        sch = schema_multi_dict

    with then:
        assert isinstance(sch, MultiDictSchema)


def test_multi_dict_empty_keys_declaration():
    with given:
        value = {}

    with when:
        sch = schema_multi_dict(value)

    with then:
        assert sch.props.keys == MultiDict()


def test_multi_dict_invalid_type_declaration_error():
    with when, raises(Exception) as exception:
        schema_multi_dict(set())

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.multi_dict` value must be an instance of "
                                        "('dict', 'list', 'MultiDict', 'MultiDictProxy'), "
                                        "instance of 'set' given")


def test_multi_dict_dict_invalid_key_declaration():
    with given:
        keys = {
            "id": schema.int(42),
            None: None,
        }

    with when, raises(Exception) as exception:
        schema_multi_dict(keys)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == ("`schema.multi_dict` value must be an instance of 'str',"
                                        " instance of 'NoneType' None given")


def test_multi_dict_dict_keys_declaration():
    with given:
        keys = {
            "id": schema.int(42),
            "name": schema.str("banana")
        }

    with when:
        sch = schema_multi_dict(keys)

    with then:
        assert sch.props.keys == MultiDict([
            ("id", schema.int(42)),
            ("name", schema.str("banana")),
        ])


def test_multi_dict_list_keys_declaration():
    with given:
        keys = [
            ("id", schema.int(42)),
            ("id", schema.str("42")),
            ("name", schema.str("banana")),
        ]

    with when:
        sch = schema_multi_dict(keys)

    with then:
        assert sch.props.keys == MultiDict(keys)


def test_multi_dict_multidict_declaration():
    with given:
        keys = MultiDict([
            ("id", schema.int(42)),
            ("id", schema.str("42")),
            ("name", schema.str("banana")),
        ])

    with when:
        sch = schema_multi_dict(keys)

    with then:
        assert sch.props.keys == keys
        assert id(sch.props.keys) != id(keys)


def test_multi_dict_multidict_proxy_declaration():
    with given:
        keys = MultiDict([
            ("id", schema.int(42)),
            ("id", schema.str("42")),
            ("name", schema.str("banana")),
        ])

    with when:
        sch = schema_multi_dict(MultiDictProxy(keys))

    with then:
        assert sch.props.keys == keys
        assert id(sch.props.keys) != id(keys)


def test_multi_dict_already_declared_declaration_error():
    with given:
        keys = {}

    with when, raises(Exception) as exception:
        schema_multi_dict(keys)(keys)

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == "`schema.multi_dict([])` is already declared"


def test_multi_dict_invalid_value_type_declaration_error():
    with when, raises(Exception) as exception:
        schema_multi_dict({"key": {}})

    with then:
        assert exception.type is DeclarationError
        assert str(exception.value) == (
            "`schema.multi_dict` value must be an instance of 'Schema', "
            "instance of 'dict' {} given"
        )
