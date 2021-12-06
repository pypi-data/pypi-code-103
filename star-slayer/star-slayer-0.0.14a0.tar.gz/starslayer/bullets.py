"""
Bullets Module. Here are stored the classes for the
different types of bullets.
"""

from typing import Optional

from .utils import Timer, SpringTimer
from .characters import Ship


BulletKwargs = dict[str, Optional[int | str | bool]]


class Bullet(Ship):
    """
    Class for defining a bullet that is shot
    from a ship, enemy or not.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int, **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'Bullet'.
        """

        # Defining default types

        if kwargs.get("health", None) == None: kwargs["health"] = 10

        super().__init__(x1, y1, x2, y2, **kwargs)
        self.accel = kwargs.get("acceleration", 1)


class BulletNormalAcc(Bullet):
    """
    A bullet of normal acceleration.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int, **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'BulletNormalAcc'.
        """

        super().__init__(x1, y1, x2, y2, **kwargs)

        oscillation_time: int = kwargs.get("oscillation_time", 30)
        self.accel_timer = Timer(oscillation_time)


    def trajectory(self) -> None:
        """
        Defines the trajectory of a normal acceleration bullet.
        """

        if self.accel_timer.current_time > 0:
            self.accel_timer.deduct(1)
            self.accel += 0.3

        self.transfer(0, -self.speed * self.accel)


class BulletSinusoidalSimple(Bullet):
    """
    A bullet of normal acceleration.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int, **kwargs: BulletKwargs) -> None:
        """
        Initializes an instance of type 'BulletSinusoidalSimple'.
        """

        super().__init__(x1, y1, x2, y2, **kwargs)

        oscillation_time: int = kwargs.get("oscillation_time", 30)
        first_to_right: bool = kwargs.get("first_to_right", True)
        self.oscillatation = SpringTimer(-oscillation_time, oscillation_time, (oscillation_time if first_to_right else -oscillation_time))


    def trajectory(self) -> None:
        """
        Defines the trajectory of a simple sinusoidal bullet.
        """

        self.oscillatation.count()
        self.transfer((self.oscillatation.current * 0.1) * self.speed, -self.speed)
