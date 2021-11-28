from baby_steps import then, when

from jj_district42 import HistoryResponseSchema


def test_history_response_declaration():
    with when:
        sch = HistoryResponseSchema()

    with then:
        assert isinstance(sch, HistoryResponseSchema)
