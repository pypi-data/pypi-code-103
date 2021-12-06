"""
Enemies Module. Contains the different types
of hostiles.
"""

from typing import Optional
from .utils import Timer, SpringTimer
from .characters import Ship


class _EnemyTypes:
    """
    A class wrapper of a dictionary for storing the
    reference to the diverse enemy types.
    """

    def __init__(self) -> None:
        """
        Creates an instance of 'EnemyTypes'.
        """

        self._enemy_types = dict()


    def __str__(self) -> str:
        """
        Displays the object info in a more human-friendly
        manner.
        """

        return str(self._enemy_types)

    
    def __getitem__(self, key: str) -> object:
        """
        Returns a value of the types based on its name.
        """

        return self._enemy_types[key]


    def get(self, key: str, default: Optional[str]=None) -> Optional[object]:
        """
        Same as '__getitem__', but with the option of addind a
        default value.
        """

        return self._enemy_types.get(key, default)


    def add_enemy(self, new_enemy: object) -> bool:
        """
        Tries to add a new enemy type to the types.

        Returns 'True' if successful, else 'False'.
        """

        if new_enemy.__name__ not in self._enemy_types:

            self._enemy_types[new_enemy.__name__] = new_enemy
            return True

        return False


    def held_enemy(self, enemy: object) -> object:
        """
        Decorator to add enemies easier.
        """

        self.add_enemy(enemy)

        return enemy


enemy_types = _EnemyTypes()


class _Enemy(Ship):
    """
    Class for defining a NPC ship that attacks
    the player.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Initializes an instance of type 'Enemy'.
        """

        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2


@enemy_types.held_enemy
class EnemyCommonA(_Enemy):
    """
    A common enemy (A version).
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Initializes an instance of type 'EnemyCommonA'.
        """

        super().__init__(x1, y1, x2, y2)

        self.hp = 3
        self.hardness = 10
        self.speed = 3

        self.internal_timer = Timer(30)
        self.direction = 0 # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"

        self.sprites = None # for now


    def trajectory(self) -> None:
        """
        Defines the movement of a common enemy (A version).
        """

        if self.internal_timer.is_zero_or_less():

            self.direction = (self.direction + 1) % 3
            self.internal_timer.reset()

        else:

            self.internal_timer.deduct(1)

        self.transfer((-self.speed if self.direction == 0 else (self.speed if self.direction == 2 else 0)),
                      ((self.speed // 2) if self.direction == 1 else 0))


@enemy_types.held_enemy
class EnemyCommonB(_Enemy):
    """
    A common enemy (B version).
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Initializes an instance of type 'EnemyCommonB'.
        """

        super().__init__(x1, y1, x2, y2)

        self.hp = 3
        self.hardness = 10
        self.speed = 3

        self.internal_timer = SpringTimer(0, 30, 30)
        self.direction = 0 # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"

        self.sprites = None # for now


    def trajectory(self) -> None:
        """
        Defines the movement of a common enemy (B version).
        """

        if self.internal_timer.current == self.internal_timer.floor:

            self.direction += 1

        elif self.internal_timer.current == self.internal_timer.ceil:

            self.direction -= 1

        elif self.internal_timer.current == self.internal_timer.ceil // 2:

            if self.internal_timer.adding:

                self.direction = (self.direction + 1) % 3

            else:

                self.direction = (self.direction + 2) % 3
        
        self.internal_timer.count()

        self.transfer((-self.speed if self.direction == 0 else (self.speed if self.direction == 2 else 0)),
                      ((self.speed // 2) if self.direction == 1 else 0))
