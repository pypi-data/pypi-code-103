"""Implement game."""

from typing import Dict, Generator, List, Tuple

Level = List[str]


def load(lines: List[str]) -> Tuple[Level, int, int]:
    """Load a level."""
    level = []
    for height, line in enumerate(lines):
        level.extend([char for char in line])
    return level, len(line), height + 1


def move(movement: Dict[str, int], key: str, level: Level) -> None:
    """Implement moves."""
    if key in movement:
        for i, tile in enumerate(level):
            if tile == "🐕":
                if level[i + movement[key]] not in "⬛🎯":
                    if level[i + movement[key]] != "　":
                        if level[i + movement[key] * 2] == "　":
                            level[i + movement[key] * 2] = level[i + movement[key]]
                        elif level[i + movement[key] * 2] == "🎯":
                            level[i + movement[key] * 2] = "　"
                        else:
                            break
                    level[i] = "　"
                    level[i + movement[key]] = "🐕"
                break


def game(
    level: Level, width: int, height: int
) -> Generator[str, str, str]:  # pragma: no cover
    """Game loop."""
    movement = {"w": -width, "d": 1, "s": width, "a": -1}
    key = yield "".join(level)
    while True:
        move(movement, key, level)
        screen = "\033[F" * (height + 1) + "".join(level)
        if "🎯" in level:
            key = yield screen
        else:
            return screen + "\nWell done!"
