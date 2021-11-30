import pytest

import must_triage.inspectors as inspectors


def test_all():
    inspector_names = list(map(lambda i: i.__name__, inspectors.all()))
    assert inspector_names == ['OCP', 'OCS']
