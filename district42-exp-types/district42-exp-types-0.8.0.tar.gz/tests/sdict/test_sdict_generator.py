from baby_steps import given, then, when
from blahblah import generate

from district42_exp_types.sdict import schema_sdict


def test_sdict_generation():
    with given:
        sch = schema_sdict

    with when:
        res = generate(sch)

    with then:
        assert isinstance(res, dict)
