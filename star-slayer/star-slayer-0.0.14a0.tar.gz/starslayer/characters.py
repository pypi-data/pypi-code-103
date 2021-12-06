"""
Characters Module. For storing playable characters
(mainly the player).
"""

from typing import Optional

from .utils import _Entity
from .consts import WIDTH, HEIGHT, GUI_SPACE

ShipVariables = Optional[int | str]
ShipDict = dict[str, ShipVariables]

class Ship(_Entity):
    """
    Class for defining a ship that
    moves on the screen.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int, **kwargs: ShipDict) -> None:
        """
        Initializes an instance of type 'Ship'.
        """

        super().__init__(x1, y1, x2, y2)

        if self.is_out_bounds(x1, y1, x2, y2):

            raise Exception(f"Coordinates ({x1}, {y1}), ({x2}, {y2}) are not valid, as they are outside of the boundaries of the screen")

        self.max_hp = kwargs.get("health", 100)
        self.hp = self.max_hp
        self.hardness = kwargs.get("how_hard", 0)
        self.speed = kwargs.get("speed", 1)
        self.sprites = kwargs.get("texture_path", None)


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return f"x1, y1, x2, y2: {self.x1}, {self.y1}, {self.x2}, {self.y2} - health: {self.hp} - hardness: {self.hardness} - speed: {self.speed} - sprites: {self.sprites}"


    def __repr__(self) -> str:
        """
        Returns a string with class information so it can be parsed 'as is' later.
        """

        return f"x1, y1, x2, y2: {self.x1}, {self.y1}, {self.x2}, {self.y2} - health: {self.hp} - hardness: {self.hardness} - speed: {self.speed} - sprites: {self.sprites}"


    def is_out_bounds(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Checks if an _Entity is out of the bounds of the screen.

        Return 'True' if so. Else returns 'False'.
        """

        width, height = WIDTH - GUI_SPACE, HEIGHT

        return any((x1 < 0, y1 < 0, x2 > width, y2 > height))


    def has_no_health(self) -> bool:
        """
        Returns 'True' if if the ship has 0 health points or less, and 'False' otherwise.
        """

        return self.hp <= 0


    def collides_with(self, other: "Ship") -> bool:
        """
        Tests if the hitbox of the ship is colliding with another given one. Returns a boolean.

        Although it is intended for other 'Ship' instances, it works with any subclass of '_Entity'.
        """

        # Test Upper Side
        if other.y1 < self.y1 < other.y2:

            # Test Upper-Left Corner
            if other.x1 < self.x1 < other.x2:

                return True
                
            # Test Upper-Right Corner
            if other.x1 < self.x2 < other.x2:

                return True

        # Test Bottom Side
        if other.y1 < self.y2 < other.y2:

            # Test Bottom-Left Corner
            if other.x1 < self.x1 < other.x2:

                return True

            # Test Bottom-Right Corner
            if other.x1 < self.x2 < other.x2:

                return True

        return False


    def transfer(self, dx: int, dy: int) -> None:
        """
        Changes ship coordinates from '(x1, y1), (x2, y2)' to '(x1 + dx, y1 + dy), (x2 + dx, y2 + dy)'.
        """

        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy


    def move(self, dx: int, dy: int) -> bool:
        """
        Moves the player around inside the boundaries of the screen.

        Returns 'False' if the atempted move is invalid, or 'True' if it is
        valid. Either way, invalid moves are ignored.
        """

        if self.is_out_bounds(self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy):

            return False

        self.transfer(dx, dy)

        return True   