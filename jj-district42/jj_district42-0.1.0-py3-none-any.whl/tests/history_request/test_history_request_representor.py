from baby_steps import given, then, when
from district42 import represent

from jj_district42 import HistoryRequestSchema


def test_history_request_representation():
    with given:
        sch = HistoryRequestSchema()

    with when:
        res = represent(sch)

    with then:
        assert res == "\n".join([
            "schema.jj_history_request(<",
            "    method=schema.str.len(1, ...),",
            "    path=schema.str,",
            "    segments=schema.dict,",
            "    params=schema.multi_dict,",
            "    headers=schema.ci_multi_dict,",
            "    body=schema.any",
            ">)",
        ])
