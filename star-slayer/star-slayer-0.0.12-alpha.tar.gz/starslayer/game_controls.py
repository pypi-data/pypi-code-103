"""
Controls Module. Processes the interactions of the player
with the game.
"""

from . import gamelib, objects, files
from .game_state import Game # Just for type hinting
from .consts import EXITING_DELAY, SPECIAL_CHARS

class GameControls:
    """
    Class for controlling the interactions with
    the game.
    """

    def __init__(self) -> None:
        """
        Initalizes an instance of type 'GameControls'.
        """

        # Control Attributes
        self.show_about = False
        self.is_changing_key = False
        self.exiting = False
        self.exit = False

        # Color Profiles
        self.selected_theme = "AZURE"
        self.color_profile = files.map_profiles()[self.selected_theme]

        # Timers
        self.exiting_cooldown = objects.Timer(EXITING_DELAY)

    def process_key(self, key: str) -> str:
        """
        Reads which key was pressed, and returns its corresponding action.
        """

        return files.map_keys().get(key)

    def process_action(self, action: str, game: Game) -> None:
        """
        Receives an action and process it into its rightful instructions.
        """

        if action:

            command = getattr(self, f"execute_{'_'.join(action.lower().split())}", None)

            # The action has a method assigned in this class
            if command: command(game)

    def execute_up(self, game: Game) -> None:
        """
        Executes the 'UP' action.

        If in-game, moves the player upwards.
        """

        if game.is_in_game:

            game.player.move(0, -game.player.speed)

    def execute_left(self, game: Game) -> None:
        """
        Executes the 'LEFT' action.

        If in-game, moves the player to the left.
        """

        if game.is_in_game:

            game.player.move(-game.player.speed, 0)

    def execute_right(self, game: Game) -> None:
        """
        Executes the 'RIGHT' action.

        If in-game, moves the player to the right.
        """

        if game.is_in_game:

            game.player.move(game.player.speed, 0)

    def execute_down(self, game: Game) -> None:
        """
        Executes the 'DOWN' action.

        If in-game, moves the player downwards.
        """

        if game.is_in_game:

            game.player.move(0, game.player.speed)

    def execute_shoot(self, game: Game) -> None:
        """
        Executes the 'SHOOT' action.

        If in-game, shoots the corresponding bullets from the player.
        """

        if game.is_in_game and game.shooting_cooldown.is_zero_or_less():

            game.shoot_bullets()
            game.shooting_cooldown.reset()

    def execute_return(self, game: Game) -> None:
        """
        Executes the 'RETURN' action.

        If in-game, it goes back to the main menu. If not, changes the current menu
        in display for its parent, if it has one.
        """

        if self.show_about:

            self.show_about = False

        elif game.is_in_game:

            game.current_menu = game.main_menu
            game.change_is_in_game()
            game.clear_assets()

        elif game.current_menu.parent and game.current_menu.press_cooldown.is_zero_or_less():

            game.current_menu.press_cooldown.reset() # First we reset the current menu
            game.current_menu = game.current_menu.parent
            game.current_menu.press_cooldown.reset() # Then the parent

    def execute_debug(self, game: Game) -> None:
        """
        Executes the 'DEBUG' action.

        If in-game, it shows debug information about the player attributes and other
        additional features.
        """

        if game.is_in_game and game.debug_cooldown.is_zero_or_less():

            game.show_debug_info = not game.show_debug_info
            game.debug_cooldown.reset()

    def execute_exit(self,game: Game) -> None:
        """
        Executes the 'EXIT' action.

        Changes an attribute of the game state so it exits the game.
        If it is in-game, it returns to the main menu instead.
        """

        if self.exiting_cooldown.is_zero_or_less():

            self.exit_game(game)

    def _translate_msg(self, message: str) -> str:
        """
        Kind of an internal function with the sole purpose of translating the rare characters
        some buttons have as their messages for a string with something more bearable. 
        """

        if message == '<':

            return "return"

        if message == "/\\":

            return "page_up"

        if message == "\/":

            return "page_down"

        if message == '^':

            return "sub_page_up"

        if message == 'v':

            return "sub_page_down"

    def process_click(self, x: int, y: int, game: Game) -> None:
        """
        Receives the coordinates of a click and process it into its rightful instructions.
        """

        if not game.is_in_game and not self.show_about:

            menu = game.current_menu

            for button in (menu.buttons_on_screen + (game.sub_menu.buttons_on_screen if game.sub_menu else [])):

                if button.x1 <= x <= button.x2 and button.y1 <= y <= button.y2:

                    if all((menu == game.controls_menu, button.msg in files.list_actions(), not game.action_to_show == button.msg)):

                        game.action_to_show = button.msg
                        game.sub_menu = game.refresh_sub_menu()

                    elif button.msg in (f"Delete {key}" for key in files.map_keys().keys()):

                        self.remove_key(button.msg.lstrip("Delete "), game)

                    elif not button.msg == "RETURN": # To avoid the button in the controls menu to overlap with the '<' ones

                        message = (self._translate_msg(button.msg) if button.msg in SPECIAL_CHARS else button.msg)
                        button_clicked = getattr(self, "click_on_" + '_'.join(message.lower().split()), None)

                        # The button has a method assigned in this class
                        if button_clicked: button_clicked(game)

                    break

    def click_on_play(self, game: Game) -> None:
        """
        Executes the 'Play' button.

        Changes the attribute 'is_in_game' of the game so it starts the game.
        """

        game.change_is_in_game()

    def click_on_options(self, game: Game) -> None:
        """
        Executes the 'Options' button.

        Changes the current menu in display for the Options Menu.
        """

        game.current_menu = game.options_menu

    def click_on_about(self, game: Game) -> None:
        """
        Executes the 'About' button.

        It overrides anything drawn on the screen to show a window with information
        about the people involved in the development of this project.        
        """

        self.show_about = True

    def click_on_exit(self, game: Game) -> None:
        """
        Executes the 'Exit' button.

        Just as the 'EXIT' action, it changes an attribute of the game so it
        tests if it exits the program.
        """

        self.exit_game(game)

    def click_on_return(self, game: Game) -> None:
        """
        Executes the 'Return' button.

        Just as the 'RETURN' action, it changes the current menu in display for its
        parent (if it exists), if in-game. If not, it changes the screen to the main
        menu.

        It is probably not the exact message that appears on the actual button, but
        something to understand its functions better. 
        """

        self.process_action("return", game)

    def click_on_page_up(self, game: Game) -> None:
        """
        Executes the 'Page Up' button.

        If able, changes the page of the current menu in display for the previous one.

        It is probably not the exact message that appears on the actual button, but
        something to understand its functions better. 
        """

        game.current_menu.change_page(False)

    def click_on_page_down(self, game: Game) -> None:
        """
        Executes the 'Page Down' button.

        If able, changes the page of the current menu in display for the next one.

        It is probably not the exact message that appears on the actual button, but
        something to understand its functions better. 
        """

        game.current_menu.change_page(True)

    def click_on_sub_page_up(self, game: Game) -> None:
        """
        Executes the (sub) 'Page Up' button.

        If able, changes the page of the current sub-menu for the previous one.

        It is probably not the exact message that appears on the actual button, but
        something to understand its functions better. 
        """

        game.sub_menu.change_page(False)

    def click_on_sub_page_down(self, game: Game) -> None:
        """
        Executes the (sub) 'Page Down' button.

        If able, changes the page of the current sub-menu for the next one.

        It is probably not the exact message that appears on the actual button, but
        something to understand its functions better. 
        """

        game.sub_menu.change_page(True)

    def click_on_configure_controls(self, game: Game) -> None:
        """
        Executes the 'Configure Controls' button.

        Changes the current menu in display for the Controls Menu
        """

        game.current_menu = game.controls_menu

    def click_on_add_key(self, game: Game) -> None:
        """
        Executes the 'Add Key' button.

        Changes the 'is_changing_key' attribute to 'True' so it adds a new key.
        """

        self.is_changing_key = True

    def add_key(self, action: str, game: Game) -> tuple[files.StrDict, bool]:
        """
        If valid, adds a key to a designed action.

        Return the dictionary of the keys, plus 'True' if the function
        succeeded, else 'False' if something happened.
        """

        event = gamelib.wait(gamelib.EventType.KeyPress)
        keys_dict = files.map_keys()
        success = False

        if event.key not in keys_dict:

            success = True

        if success:

            keys_dict[event.key] = action
            files.print_keys(keys_dict)
            game.sub_menu = game.refresh_sub_menu()

        self.is_changing_key = False

    def remove_key(self, key: str, game: Game) -> None:
        """
        Removes the key passed as an argument from the keys dictionary.
        """
        keys_dict = files.map_keys()

        if key in keys_dict:

            value = keys_dict[key]
            keys_dict.pop(key)

            if not files.list_repeated_keys(value, keys_dict):

                keys_dict['/'] = value

            files.print_keys(keys_dict)
            game.sub_menu = game.refresh_sub_menu()

    def refresh(self, keys_dict: dict[str, bool]) -> None:
        """
        Takes the actions that must be done in each iteration of a loop, like
        refreshing or counting timers.

        It takes a dictionary of the keys pressed to decide if it counts some timers.
        """
        correct_keys = files.list_repeated_keys("EXIT", files.map_keys())

        if any(keys_dict.get(key, False) for key in correct_keys):

            self.exiting = True
            self.exiting_cooldown.deduct(1)

        else:

            self.exiting = False
            self.exiting_cooldown.reset()

    def exit_game(self, game: Game) -> None:
        """
        Sets the control variable 'self.exiting' to 'True' to see if it exits
        the game.
        """
        if game.is_in_game:

            self.process_action("RETURN", game)
            self.exiting_cooldown.reset()

        else:

            self.exit = True