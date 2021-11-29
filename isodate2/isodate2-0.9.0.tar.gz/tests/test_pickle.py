"""
Tests to parse an ISO datetime string into a datetime object.
"""
import pickle

import pytest

import isodate


@pytest.mark.parametrize("proto", list(range(0, pickle.HIGHEST_PROTOCOL + 1)))
def test_pickle_datetime(proto):
    """
    Parse an ISO datetime string and compare it to the expected value.
    """
    dti = isodate.parse_datetime("2012-10-26T09:33+00:00")
    pikl = pickle.dumps(dti, proto)
    assert dti == pickle.loads(pikl), f"pickle proto {proto} failed"


@pytest.mark.parametrize("proto", list(range(0, pickle.HIGHEST_PROTOCOL + 1)))
def test_pickle_duration(proto):
    """
    Pickle / unpickle duration objects.
    """
    from isodate.duration import Duration

    dur = Duration()
    pikl = pickle.dumps(dur, proto)
    assert dur == pickle.loads(pikl)


def test_pickle_utc():
    """
    isodate.UTC objects remain the same after pickling.
    """
    assert isodate.UTC is pickle.loads(pickle.dumps(isodate.UTC))
