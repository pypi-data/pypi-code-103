"""
Logics Module. Its purpose is to control the logic behaviour
of the game.
"""

from typing import Optional

from . import utils, characters, bullets, enemies, files
from .consts import PLAYER_DAMAGED_SPRITE, PLAYER_SPRITE, PROFILES_CHANGER, PROFILES_DELETER, SUB_MENU_LEFT, SUB_MENU_RIGHT, WIDTH, HEIGHT

corners_tuple = tuple[int | float, int | float, int | float, int | float]


class Game:
    """
    Class for the Game itself.
    """

    def __init__(self, inital_power: int=1, cooldown_constant: int=30) -> None:
        """
        Initalizes an instance of type 'Game'.
        """

        width, height = WIDTH, HEIGHT

        main_x1 = int(width / 3.75)
        main_y1 = int(height / 2)
        main_x2 = int(width / 1.363636)
        main_y2 = int(height / 1.076923)
        main_coords = (main_x1, main_y1, main_x2, main_y2)

        # Menus
        self.main_menu = utils.Menu(["Play", "Options", "About", "Exit"],
                                      main_coords)

        self.options_menu = utils.Menu(["Configure Controls", "Change Color Profile"],
                                         main_coords,
                                         max_rows=4, parent_menu=self.main_menu)

        self.controls_menu = utils.Menu(files.list_actions(),
                                        ((width // 75), (height // 5), int(width / 4.237288), int(height / 1.014492)),
                                        max_rows=8, parent_menu=self.options_menu)

        self.profiles_menu = utils.Menu(files.list_profiles() + ["+"],
                                        (int(width / 1.25), int(height / 5.185185), int(width / 1.013513), int(height / 1.076923)),
                                        max_rows=10, special_btn_on_right=False, parent_menu=self.options_menu)

        self._menu_in_display = self.main_menu

        # Sub-menu related
        self.action_to_show = files.list_actions()[0]
        self.sub_menu = None

        # Level Parameters
        self.game_level = 1
        self.level_dict = files.map_level(1)
        self.level_timer = utils.Timer(self.level_dict["total_time"])
        self.level_dict.pop("total_time")

        # Player Parameters
        self.player = characters.Ship((width // 2) - 30, int(height / 1.17) - 30, (width // 2) + 30, int(height / 1.17) + 30,
                                    how_hard=1, speed=5, texture_path=(PLAYER_SPRITE, PLAYER_DAMAGED_SPRITE))
        self.power_level = inital_power

        # Color Profiles
        self.color_profiles = files.map_profiles()
        self._color_theme = files.list_profiles()[0]
        self.color_profile = self.color_profiles[self._color_theme]

        # Timers
        self.cool_cons = cooldown_constant
        self.invulnerability = utils.Timer(50 + (self.power_level * 5))
        self.shooting_cooldown = utils.Timer(self.cool_cons // self.power_level)
        self.debug_cooldown = utils.Timer(20)
        
        # Enemies, Misc
        self.enemies, self.bullets = list(), list()

        # Control Booleans
        self.is_in_game = False
        self.show_debug_info = False


    @property
    def selected_theme(self) -> str:
        """
        Returns the current color theme (name only).
        """

        return self._color_theme


    @selected_theme.setter
    def selected_theme(self, new_value: str) -> None:
        """
        If the selected theme changes, then the profile should also do it.
        """

        real_name = '_'.join(new_value.upper().split())

        if real_name in self.color_profiles:

            self._color_theme = real_name
            self.color_profile = self.color_profiles[real_name]


    @property
    def current_menu(self) -> Optional[utils.Menu]:
        """
        Returns the current menu in display.
        """

        return self._menu_in_display


    @current_menu.setter
    def current_menu(self, new_menu: Optional[utils.Menu]=None) -> None:
        """
        Changes the current menu in display for the one passed as an argument.
        """

        self._menu_in_display = new_menu

        new_sub_menu = None

        if new_menu is self.controls_menu:

            new_sub_menu = self.refresh_controls_sub_menu()

        elif new_menu is self.profiles_menu:

            new_sub_menu = self.refresh_profiles_sub_menu()

        self.sub_menu = new_sub_menu


    def refresh_controls_sub_menu(self, corners: corners_tuple=SUB_MENU_RIGHT) -> utils.Menu:
        """
        Refreshes a mini menu made of buttons of the keys of the action to show.
        It then returns it, to be assigned elsewhere.
        """

        if not len(corners) == 4:

            raise Exception(f"corners has {len(corners)} values. It must be 4 integers or floats.")

        repeated_keys = files.list_repeated_keys(self.action_to_show, files.map_keys())
        changeable_keys = list()

        for key in repeated_keys:

            if not key == '/':

                changeable_keys.append(f"Delete {key}")

        changeable_keys.append("Add Key")

        return utils.Menu.sub_menu(changeable_keys, corners,
                                   how_many_columns=2, space_between=20)


    def refresh_profiles_sub_menu(self, corners: corners_tuple=SUB_MENU_LEFT) -> utils.Menu:
        """
        Refreshes a mini menu where are stored the profiles of the game.
        """

        if not len(corners) == 4:

            raise Exception(f"corners has {len(corners)} values. It must be 4 integers or floats.")

        profile_atts = [PROFILES_CHANGER, PROFILES_DELETER] + files.list_attributes(self.color_profile)

        return utils.Menu.sub_menu(profile_atts, corners,
                                   max_rows=7, how_many_columns=2, space_between_x=20, space_between_y=15, button_anchor='w', special_btn_on_right=False)


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

        player_center_x = self.player.center[0]

        match self.power_level:

            case 1:

                self.bullets.append(bullets.BulletNormalAcc(player_center_x - 5, self.player.y1 + 30, player_center_x + 5, self.player.y1 + 20,
                                    how_hard=self.player.hardness, speed=2))

            case 2:

                self.bullets.append(bullets.BulletSinusoidalSimple(player_center_x - 5, self.player.y1 + 30, player_center_x + 5, self.player.y1 + 20,
                                    how_hard=self.player.hardness, speed=3, first_to_right=True))

            case 3:

                self.bullets.append(bullets.BulletSinusoidalSimple(player_center_x - 15, self.player.y1 + 30, player_center_x -5, self.player.y1 + 20,
                                    how_hard=self.player.hardness, speed=3, first_to_right=True))

                self.bullets.append(bullets.BulletSinusoidalSimple(player_center_x + 5, self.player.y1 + 30, player_center_x + 15, self.player.y1 + 20,
                                    how_hard=self.player.hardness, speed=3, first_to_right=False))


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

                    enemy_type_to_add = enemies.enemy_types.get(action["type"], enemies.EnemyCommonA)

                    self.enemies.append(enemy_type_to_add(action["x1"], action["y1"], action["x2"], action["y2"]))
                
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
