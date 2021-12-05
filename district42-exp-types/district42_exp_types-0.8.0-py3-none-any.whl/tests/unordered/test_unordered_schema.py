from baby_steps import then, when

from district42_exp_types.unordered import UnorderedSchema, unordered_schema


def test_unordered_declaration():
    with when:
        sch = unordered_schema

    with then:
        assert isinstance(sch, UnorderedSchema)
