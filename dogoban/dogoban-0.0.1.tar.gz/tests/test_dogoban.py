"""Test game."""

from dogoban import load, move


def test_load() -> None:
    """Test loading a level."""
    assert load(["abc", "def"]) == (["a", "b", "c", "d", "e", "f"], 3, 2)


def test_move() -> None:
    """Test making a move."""
    move({"t": -1}, "t", ["."])
    level = ["⬛", "　", ".", "　", "🐕"]
    move({"t": -1}, "n", level)
    assert level == ["⬛", "　", ".", "　", "🐕"]
    move({"t": -1}, "t", level)
    assert level == ["⬛", "　", ".", "🐕", "　"]
    move({"t": -1}, "t", level)
    assert level == ["⬛", ".", "🐕", "　", "　"]
    move({"t": -1}, "t", level)
    assert level == ["⬛", ".", "🐕", "　", "　"]


def test_no_enter_target() -> None:
    """Test dog can not enter target."""
    level = ["🎯", "🐕"]
    move({"t": -1}, "t", level)
    assert level == ["🎯", "🐕"]


def test_match() -> None:
    """Test everything else can enter target."""
    level = ["🎯", ".", "🐕"]
    move({"t": -1}, "t", level)
    assert level == ["　", "🐕", "　"]
