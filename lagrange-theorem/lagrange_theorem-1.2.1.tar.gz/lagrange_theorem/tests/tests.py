from ..calculate_numbers import calculate_numbers


def test_func_little_numbers():
    assert calculate_numbers(1, 5) == [(1, (1, 0, 0, 0)),
                                       (2, (1, 1, 0, 0)),
                                       (3, (1, 1, 1, 0)),
                                       (4, (2, 0, 0, 0))]


def test_func_big_numbers():
    assert calculate_numbers(572, 575) == [(572, (21, 11, 3, 1)),
                                           (573, (20, 13, 2, 0)),
                                           (574, (23, 6, 3, 0))]


def test_func_one_number():
    assert calculate_numbers(1523, 1524) == [(1523, (39, 1, 1, 0))]


def test_func_one_big_number():
    assert calculate_numbers(1523, 1524) == [(1523, (39, 1, 1, 0))]


def test_func_other_numbers():
    assert calculate_numbers(8, 12) == [(8, (2, 2, 0, 0)),
                                        (9, (3, 0, 0, 0)),
                                        (10, (3, 1, 0, 0)),
                                        (11, (3, 1, 1, 0))]
    assert calculate_numbers(572, 575) == [(572, (21, 11, 3, 1)),
                                           (573, (20, 13, 2, 0)),
                                           (574, (23, 6, 3, 0))]


