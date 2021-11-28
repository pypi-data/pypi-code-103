from baby_steps import then, when

from jj_district42 import HistoryRequestSchema


def test_history_request_declaration():
    with when:
        sch = HistoryRequestSchema()

    with then:
        assert isinstance(sch, HistoryRequestSchema)
