from rhubarbpy import loopsum, fibonacci
from rhubarbpy.subpkg import subpkg_hello


def test_function_runs():
    loopsum([1, 2, 3])
    assert True
