"""
Logics Module. Its purpose is to control the logic behaviour
of the game.
"""

from typing import Optional

from . import objects, files
from .consts import PLAYER_DAMAGED_SPRITE, PLAYER_SPRITE, WIDTH, HEIGHT


class Game:
    """
    Class for the Game itself.
    """

    def __init__(self, inital_power: int=1, cooldown_constant: int=30) -> None:
        """
        Initalizes an instance of type 'Game'.
        """

        width, height = WIDTH, HEIGHT

        # Menus
        self.main_menu = objects.Menu(["Play", "Options", "About", "Exit"],
                         (200, height // 2, width - 200, height - 50))

        self.options_menu = objects.Menu(["Configure Controls", "Change Color Profile (WIP)"],
                                    (200, height // 2, width - 200, height - 50), max_rows=4, parent_menu=self.main_menu)

        self.controls_menu = objects.Menu(files.list_actions(),
                                    (10, (height // 5), (width // 4) - 10, height - 10), max_rows=8, parent_menu=self.options_menu)

        self._menu_in_display = self.main_menu

        # Sub-menu related
        self.action_to_show = files.list_actions()[0]
        self.sub_menu = self.refresh_sub_menu()

        # Level Parameters
        self.game_level = 1
        self.level_dict = files.map_level(1)
        self.level_timer = objects.Timer(self.level_dict["total_time"])
        self.level_dict.pop("total_time")

        # Player Parameters
        self.player = objects.Ship((width // 2) - 30, int(height / 1.17) - 30, (width // 2) + 30, int(height / 1.17) + 30,
                                    how_hard=1, speed=5, texture_path=(PLAYER_SPRITE, PLAYER_DAMAGED_SPRITE))
        self.power_level = inital_power
        
        # Timers
        self.cool_cons = cooldown_constant
        self.invulnerability = objects.Timer(50 + (self.power_level * 5))
        self.shooting_cooldown = objects.Timer(self.cool_cons // self.power_level)
        self.debug_cooldown = objects.Timer(20)
        
        # Enemies, Misc
        self.enemies, self.bullets = list(), list()

        # Control Booleans
        self.is_in_game = False
        self.show_debug_info = False

    @property
    def current_menu(self) -> Optional[objects.Menu]:
        """
        Returns the current menu in display.
        """

        return self._menu_in_display

    @current_menu.setter
    def current_menu(self, new_menu: Optional[objects.Menu]=None) -> None:
        """
        Changes the current menu in display for the one passed as an argument.
        """

        self._menu_in_display = new_menu

        self.sub_menu = (None if new_menu is not self.controls_menu else self.refresh_sub_menu())

    def refresh_sub_menu(self, x1: int | float=(WIDTH * 0.29),
                            y1: int | float=(HEIGHT // 2),
                            x2: int | float=(WIDTH * 0.96),
                            y2: int | float=(HEIGHT - 10)) -> objects.Menu:
        """
        Refreshes a mini menu made of buttons of the keys of the action to show.
        It then returns it, to be assigned elsewhere.
        """

        repeated_keys = files.list_repeated_keys(self.action_to_show, files.map_keys())
        changeable_keys = list()

        for key in repeated_keys:

            if not key == '/':

                changeable_keys.append(f"Delete {key}")

        changeable_keys.append("Add Key")

        return objects.Menu.sub_menu(changeable_keys, (x1, y1, x2, y2), how_many_cols=2, space=20)

    def level_up(self, how_much: int=1) -> None:
        """
        Increments by 'how_much' the level of the game.
        """

        self.game_level += how_much
        self.level_dict = files.map_level(self.game_level)

    def power_up(self, how_much: int=1) -> None:
        """
        Increments by 'how_much' the power of the player.
        """

        self.power_level += how_much
        self.shooting_cooldown.initial_time = self.cool_cons // self.power_level

    def shoot_bullets(self) -> None:
        """
        Shoots bullets from player.
        """

        player_center_x = self.player.center()[0]

        if self.power_level  == 1:

            self.bullets.append(objects.Bullet(player_center_x - 5, self.player.y1 + 30, player_center_x + 5, self.player.y1 + 20,
                                how_hard=self.player.hardness, speed=2))

        elif self.power_level == 2:

            self.bullets.append(objects.Bullet(player_center_x - 5, self.player.y1 + 30, player_center_x + 5, self.player.y1 + 20,
                                how_hard=self.player.hardness, speed=3, bullet_type="sinusoidal_simple", first_to_right=True))

        elif self.power_level == 3:

            self.bullets.append(objects.Bullet(player_center_x - 15, self.player.y1 + 30, player_center_x -5, self.player.y1 + 20,
                                how_hard=self.player.hardness, speed=3, bullet_type="sinusoidal_simple", first_to_right=True))

            self.bullets.append(objects.Bullet(player_center_x + 5, self.player.y1 + 30, player_center_x + 15, self.player.y1 + 20,
                                how_hard=self.player.hardness, speed=3, bullet_type="sinusoidal_simple", first_to_right=False))

    def exec_bul_trajectory(self) -> None:
        """
        Moves each bullet according to their trajectory.
        """

        for bullet in self.bullets:

            if self.player.collides_with(bullet):

                if bullet.hardness > self.player.hardness:

                    self.player.hp -= bullet.hardness
                    bullet.hp = 0

            for enem in self.enemies:

                if bullet.collides_with(enem):

                    enem.hp -= bullet.hardness
                    bullet.hp = 0
                    break

            if bullet.y2 < -100 or bullet.has_no_health():

                self.bullets.remove(bullet)

            bullet.trajectory()

    def exec_enem_trajectory(self) -> None:
        """
        Moves each enemy according to its defined behaviour.
        """

        for enem in self.enemies:
            
            if enem.collides_with(self.player):

                if self.invulnerability.is_zero_or_less():

                    self.player.hp -= enem.hardness
                    self.invulnerability.reset()

            if enem.has_no_health() or enem.y1 > HEIGHT + 100:

                self.enemies.remove(enem)

            enem.trajectory()

    def exec_lvl_script(self) -> None:
        """
        Reads the level dictionary timeline and executes the instructions detailed within.
        """

        for instant in self.level_dict:

            if int(instant) == self.level_timer.current_time:

                for action in self.level_dict[instant]:

                    self.enemies.append(objects.Enemy(action['x1'], action['y1'], action['x2'], action['y2'], action['type']))
                
                self.level_dict.pop(instant)
                break

    def clear_assets(self) -> None:
        """
        Clears all enemies and bullets in their lists once returned to the main menu.
        """

        self.enemies = list()
        self.bullets = list()

    def advance_game(self) -> None:
        """
        This function is that one of a wrapper, and advances the state of the game.
        """

        if self.is_in_game:

            self.current_menu = None

            self.exec_bul_trajectory()
            self.exec_enem_trajectory()
            self.exec_lvl_script()

            self.refresh_timers()

        else:

            self.show_debug_info = False

            if not self._menu_in_display.press_cooldown.is_zero_or_less():

                self._menu_in_display.press_cooldown.deduct(1)

    def refresh_timers(self) -> None:
        """
        Refreshes all the timers of the game, so that it updates theirs values.
        """

        if not self.level_timer.is_zero_or_less():

            self.level_timer.deduct(1)

        if not self.shooting_cooldown.is_zero_or_less():

            self.shooting_cooldown.deduct(1)

        if not self.debug_cooldown.is_zero_or_less():

            self.debug_cooldown.deduct(1)

        if not self.invulnerability.is_zero_or_less():

            self.invulnerability.deduct(1)

    def change_is_in_game(self) -> None:
        """
        Changes 'self.is_in_game' to its opposite.
        """

        self.is_in_game = not self.is_in_game