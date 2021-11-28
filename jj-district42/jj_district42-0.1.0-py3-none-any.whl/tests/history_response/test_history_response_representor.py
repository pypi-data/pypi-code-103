from baby_steps import given, then, when
from district42 import represent

from jj_district42 import HistoryResponseSchema


def test_history_response_representation():
    with given:
        sch = HistoryResponseSchema()

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
            "schema.jj_history_response(<",
            "    status=schema.int.min(1),",
            "    reason=schema.str,",
            "    headers=schema.ci_multi_dict,",
            "    body=schema.any",
            ">)",
        ])
