import pytest

import must_triage.inspectors.util as util


class TestMergeInterests:
    @pytest.mark.parametrize(
        "existing,new,expected",
        [
            (
                dict(foo=['foo']),
                dict(bar=['bar']),
                dict(foo=['foo'], bar=['bar']),
            ),
            (
                dict(foo=['1']),
                dict(foo=['2']),
                dict(foo=['1', '2']),
            ),
            (
                dict(foo=['foo']),
                dict(bar=[]),
                dict(foo=['foo']),
            )
        ]
    )
    def test_merge(self, existing, new, expected):
        assert util.merge_interests(existing, new) == expected
