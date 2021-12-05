from baby_steps import given, then, when
from blahblah import generate
from district42 import schema
from multidict import CIMultiDict

from district42_exp_types.ci_multi_dict import schema_ci_multi_dict


def test_ci_multi_dict_empty_generation():
    with given:
        sch = schema_ci_multi_dict

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, CIMultiDict)


def test_ci_multi_dict_generation():
    with given:
        sch = schema_ci_multi_dict([
            ("key", schema.str("banana")),
            ("Key", schema.int(42)),
        ])

    with when:
        res = generate(sch)

    with then:
        assert res == CIMultiDict([
            ("key", "banana"),
            ("Key", 42),
        ])
