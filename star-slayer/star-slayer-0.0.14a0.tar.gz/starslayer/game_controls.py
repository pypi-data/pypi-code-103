"""
Controls Module. Processes the interactions of the player
with the game.
"""

from typing import Optional

from . import gamelib, files
from .utils import Timer
from .game_state import Game # Just for type hinting
from .consts import DEFAULT_THEME, EXITING_DELAY, NEW_THEME, SPECIAL_CHARS

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
        self.is_on_prompt = False
        self.exiting = False
        self.exit = False

        # Timers
        self.exiting_cooldown = Timer(EXITING_DELAY)


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

        else:

            if game.sub_menu:

                self.click_on_sub_page_up(game)

            else:

                self.click_on_page_up(game)


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

        else:

            if game.sub_menu:

                self.click_on_sub_page_down(game)

            else:

                self.click_on_page_down(game)


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

        match message:

            case '<':

                return "return"

            case "/\\":

                return "page_up"

            case "\\/":

                return "page_down"

            case '^':

                return "sub_page_up"

            case 'v':

                return "sub_page_down"

            case '+':

                return "add_profile"


    def process_click(self, x: int, y: int, game: Game) -> None:
        """
        Receives the coordinates of a click and process it into its rightful instructions.
        """

        if not game.is_in_game and not self.show_about:

            menu = game.current_menu

            for button in (menu.buttons_on_screen + (game.sub_menu.buttons_on_screen if game.sub_menu else [])):

                if button.x1 <= x <= button.x2 and button.y1 <= y <= button.y2:

                    if all((menu is game.controls_menu, button.msg in files.list_actions(), not game.action_to_show == button.msg)):

                        game.action_to_show = button.msg
                        game.sub_menu = game.refresh_controls_sub_menu()

                    elif all((menu is game.profiles_menu, button.msg in files.list_profiles(), not game.selected_theme == button.msg)):

                        game.selected_theme = button.msg
                        game.sub_menu = game.refresh_profiles_sub_menu()

                    elif all((menu is game.profiles_menu, button.msg in files.list_attributes(game.color_profile))):

                        self.select_att_color(button.msg, game)

                    elif button.msg in (f"Delete {key}" for key in files.map_keys()):

                        self.remove_key(button.msg.removeprefix("Delete "), game)

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

        Changes the 'is_on_prompt' attribute to 'True' so it adds a new key.
        """

        self.is_on_prompt = True


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
            game.sub_menu = game.refresh_controls_sub_menu()

        self.is_on_prompt = False


    def remove_key(self, key: str, game: Game) -> Optional[str]:
        """
        Removes the key passed as an argument from the keys dictionary.

        Returns the removed key if available.
        """
        keys_dict = files.map_keys()

        if key in keys_dict:

            value = keys_dict.pop(key)

            if not files.list_repeated_keys(value, keys_dict):

                keys_dict['/'] = value

            files.print_keys(keys_dict)
            game.sub_menu = game.refresh_controls_sub_menu()

            return key


    def click_on_change_color_profile(self, game: Game) -> None:
        """
        Changes the color theme of the game.
        """

        game.current_menu = game.profiles_menu


    def click_on_change_profile_name(self, game: Game) -> None:
        """
        Changes the name of the color profile.
        """

        new_name = '_'.join(gamelib.input("Please enter the new Profile Name").upper().split())

        if new_name == '':

            gamelib.say("Name not valid")
            return

        elif new_name in files.list_profiles(game.color_profiles):

            gamelib.say("Name already used")
            return

        game.color_profiles[new_name] = game.color_profiles.pop(game.selected_theme)
        files.print_profiles(game.color_profiles)

        game.selected_theme = new_name
        self.refresh_menu(game)


    def click_on_add_profile(self, game: Game) -> None:
        """
        Adds a new color profile, and it is initally identical to the hidden
        profile 'DEFAULT'.
        """

        repeated_new_ones = [profile for profile in files.list_profiles(game.color_profiles) if profile.startswith(NEW_THEME)]
        new_theme_name = f"{NEW_THEME}_{len(repeated_new_ones) + 1}"

        game.color_profiles[new_theme_name] = game.color_profiles[DEFAULT_THEME]
        files.print_profiles(game.color_profiles)

        game.selected_theme = new_theme_name
        self.refresh_menu(game)


    def click_on_delete_this_profile(self, game: Game) -> Optional[files.StrDict]:
        """
        Deletes the current profile, if it is not the last one.

        Returns the deleted profile if available.
        """

        if len(game.color_profiles) == 2: # +1 for the hidden theme

            gamelib.say("You cannot delete this color profile, as it is the only one remaining.")
            return

        old_theme_name = game.selected_theme
        old_theme = game.color_profiles.pop(game.selected_theme)

        files.print_profiles(game.color_profiles)

        game.selected_theme = files.list_profiles(game.color_profiles)[0]
        self.refresh_menu(game)

        return {old_theme_name : old_theme}


    def select_att_color(self, attribute: str, game: Game) -> None:
        """
        Prompts the user to select a new color.
        """

        print(f"\n{attribute = }\n")


    def refresh_menu(self, game: Game) -> None:
        """
        Resfreshes the current menu buttons.
        """

        game.current_menu.change_buttons(files.list_profiles(game.color_profiles) + ["+"])
        game.sub_menu = game.refresh_profiles_sub_menu()


    def prompt(self, game: Game) -> None:
        """
        Processes the action to prompt the user.
        """

        if game.current_menu is game.controls_menu:

            self.add_key(game.action_to_show, game)

        elif game.current_menu is game.profiles_menu:

            ...


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