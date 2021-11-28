from my_lib.src.foo import left_pad


def test_foo01():
    assert '  foo' == left_pad('foo', 5)


def test_foo02():
    assert '  foo' != left_pad('foo', 6)
