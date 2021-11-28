from dataclasses import dataclass

from takes.takes import takes


@dataclass
class Point:
    x: int = 0
    y: int = 0


def test_replace_first_pos_only_arg_by_name():
    @takes(Point, name="pos_only_1")
    def test(pos_only_1, pos_only_2, /):
        assert isinstance(pos_only_1, Point)

    test({"x": 1, "y": 1}, 1)


def test_replace_second_pos_only_arg_by_name():
    @takes(Point, name="pos_only_2")
    def test(pos_only_1, pos_only_2, /):
        assert isinstance(pos_only_2, Point)

    test(1, {"x": 1, "y": 1})
