"""
Objects Module. Contains various datatypes utilized
in the game.
"""

from typing import Optional

from .consts import WIDTH, HEIGHT

StrList = list[str]
IntTuple = tuple[int, int, int, int]

MenuVariables = Optional[int | bool]
MenuDict = dict[str, MenuVariables]


class _Entity:
    """
    Generic class for defining a bounding box.

    This is a basic class that is not used by itself.
    It serves as superclass of many others.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Initializes an instance of type '_Entity'.

        It should always be true that 'x1 <= x2 && y1 <= y2'. If
        it is not the case, those variables are inverted.
        """

        if x1 > x2:

            x1, x2 = x2, x1

        if y1 > y2:

            y1, y2 = y2, y1

        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2


    def all_coord(self) -> IntTuple:
        """
        Returns a tuple with all the coordiantes of its hitbox.
        """

        return self.x1, self.y1, self.x2, self.y2


    @property
    def upper_left(self) -> IntTuple:
        """
        Returns the UPPER LEFT coordinates of its hitbox.
        """

        return self.x1, self.y1


    @property
    def upper_right(self) -> IntTuple:
        """
        Returns the UPPER RIGHT coordinates of its hitbox.
        """

        return self.x1, self.y1


    @property
    def bottom_left(self):
        """
        Returns the BOTTOM LEFT coordinates of its hitbox.
        """

        return self.x1, self.y2


    @property
    def bottom_right(self) -> IntTuple:
        """
        Returns the BOTTOM RIGHT coordinates of its hitbox.
        """

        return self.x2, self.y2


    @property
    def center(self) -> IntTuple:
        """
        Return the CENTER coordinates of its hitbox.
        """

        return ((self.x2 + self.x1) // 2), ((self.y2 + self.y1) // 2)


    @property
    def width(self) -> int:
        """
        Returns the WIDTH of its hitbox.
        """

        return self.x2 - self.x1


    @property
    def height(self) -> int:
        """
        Returns the HEIGHT of its hitbox.
        """

        return self.y2 - self.y1


class Button(_Entity):
    """
    Class for defining a hitbox of a button and
    a message it can carry.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int, message: str='') -> None:
        """
        Initializes an instance of type 'Button'.
        """

        super().__init__(x1, y1, x2, y2)
        self.msg = message


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return self.msg


    def is_inside(self, x: int, y: int) -> bool:
        """
        Returns 'True' if some given coordinates are inside the hitbox
        of this button.
        """

        return (self.x1 <= x <= self.x2) and (self.y1 <= y <= self.y2)


ButtonsList = list[Button]


class Menu:
    """
    Class for defining a game menu.
    """

    def __init__(self, button_titles: StrList, area_corners: IntTuple, **kwargs: MenuDict) -> None:
        """
        Initializes an instance of type 'Menu'.

        The following kwargs are the only valid:

        'button_titles' must be a non-empty tuple.

        'area_corners' must be a tuple of exactly 4 integers as its values.

        -

        And the kwargs:

        'max_rows' cannot be an integer lower than 1.

        'how_many_columns' is the the number of columns to be used.

        'space_between' is the default value for dead space between buttons.

        'space_between_x' is the horizontal value for dead space between
        buttons. If not provided, it defaults to 'space between'.

        'space_between_y' is the vertical value for dead space between buttons.
        If not provided, it defaults to 'space between'.

        'parent_menu' is another instance of type 'Menu' that has this instance
        as its child.

        'force_button_resize' means if the menu must use all the space in the area
        it is specified, which can resize the buttons.

        'special_btn_on_right' means if the buttons for pages navigation should be
        on the right or left of the menu.

        'button_anchor' refers to the point from which the text of each button is
        generated. It can be any combination of two chars from 'n' - 'w' - 'e' - 's';
        otherwise it can also be 'c'.

        'offset_x' is the offset to be used in the X coordinate, if 'button_anchor' is 'c'.

        'offset_y' is the offset to be used in the Y coordinate, if 'button_anchor' is 'c'.
        """

        if button_titles == ():

            raise Exception("'button_titles' cannot be empty. Must be an iteration with names (strings) and must have a length of at least 1.")

        # Define default values
        max_rows: int = kwargs.get("max_rows", 4)
        how_many_columns: int = kwargs.get("how_many_columns", 1)
        self.space_between: int = kwargs.get("space_between", 10)
        self.space_between_x: int = kwargs.get("space_between_x", self.space_between)
        self.space_between_y: int = kwargs.get("space_between_y", self.space_between)
        parent_menu: Optional["Menu"] = kwargs.get("parent_menu", None)
        force_button_resize: bool = kwargs.get("force_button_resize", False)
        special_btn_on_right: bool = kwargs.get("special_btn_on_right", True)

        # Graphics-related
        self.button_anchor: str = kwargs.get("button_anchor", 'c')

        self.offset_x: int = kwargs.get("offset_x", 0)
        self.offset_y: int = kwargs.get("offset_y", 0)

        if max_rows < 1:

            raise Exception("'max_rows' must be an integer of 1 or higher.")

        if not len(area_corners) == 4:

            raise Exception(f"area_corners has {len(area_corners)} values. It must have exactly 4 integers as values.")

        button_titles = (button_titles.split("-=trash_value=-") if isinstance(button_titles, str) else list(button_titles))

        buttons_len = len(button_titles)

        how_many_rows = ((buttons_len // how_many_columns) if any((how_many_columns == 1, buttons_len % how_many_columns == 0)) else (buttons_len // how_many_columns) + 1)

        if force_button_resize and how_many_rows < max_rows:

            max_rows = how_many_rows

        # Measures
        self.area_x1, self.area_y1, self.area_x2, self.area_y2 = area_corners
        self.max_columns = how_many_columns
        self.max_rows = max_rows

        self.x_space = (self.area_x2 - self.area_x1) // self.max_columns
        self.y_space = (self.area_y2 - self.area_y1) // self.max_rows

        # Pages-related calculations
        self.max_pages = (((how_many_rows // self.max_rows) + 1) if all((not how_many_rows == self.max_rows, not how_many_rows % self.max_rows == 0)) else how_many_rows // self.max_rows)
        self.current_page = 1

        # Menu-related
        self.parent = parent_menu

        # Special Buttons

        special_x1 = ((self.area_x2 + self.space_between) if special_btn_on_right else (self.area_x1 - (self.y_space // 2)))
        special_x2 = ((self.area_x2 + (self.y_space // 2)) if special_btn_on_right else (self.area_x1 - self.space_between_y))

        self.pgup_button = Button(special_x1,
                                  self.area_y1,
                                  special_x2,
                                  (self.area_y1 + (self.y_space // 2)), "/\\")
        self.pgdn_button = Button(special_x1,
                                  (self.area_y2 - (self.y_space // 2)),
                                  special_x2,
                                  self.area_y2, "\/")
        self.return_button = Button(self.area_x1,
                                    self.area_y1 - (HEIGHT // 20),
                                    self.area_x1 + (WIDTH // 20),
                                    self.area_y1 - self.space_between_y, '<')

        # Button Lists
        self._buttons = self.generate_buttons(button_titles)
        self.buttons_on_screen = self.update_buttons()

        # Timers
        self.press_cooldown = Timer(20)


    @property
    def buttons(self) -> ButtonsList:

        return self._buttons

    @buttons.setter
    def buttons(self, new_buttons: ButtonsList) -> None:

        self._buttons = new_buttons
        self.buttons_on_screen = self.update_buttons()


    @classmethod
    def sub_menu(cls, button_titles: StrList, corners: IntTuple, **kwargs: MenuDict) -> "Menu":
        """
        It creates an instance of type 'Menu', but with the symbols for some buttons
        changed.
        """

        sub = cls(button_titles, corners, **kwargs)

        sub.pgup_button.msg = '^'
        sub.pgdn_button.msg = 'v'

        return sub


    def generate_buttons(self, titles_list: StrList) -> ButtonsList:
        """
        Generate buttons based on the effective area of the menu and the 'self.button_titles' list.
        'space_between' determines how much dead space there is between each button in said area.
        """

        buttons_list = list()
        cols_counter = 0
        rows_counter = 0

        for title in titles_list:

            cols_counter %= self.max_columns
            rows_counter %= self.max_rows

            x1 = (cols_counter * self.x_space) + self.area_x1 + (0 if cols_counter == 0 else self.space_between_x // 2)
            x2 = ((cols_counter + 1) * self.x_space) + self.area_x1 - (0 if cols_counter == (self.max_columns - 1) else self.space_between_x // 2)
            y1 = (rows_counter * self.y_space) + self.area_y1 + (0 if rows_counter == 0 else self.space_between_y // 2)
            y2 = ((rows_counter + 1) * self.y_space) + self.area_y1 - (0 if rows_counter == (self.max_rows - 1) else self.space_between_y // 2)

            buttons_list.append(Button(x1, y1, x2, y2, title))

            cols_counter += 1

            if cols_counter % self.max_columns == 0: # Go to next row only if the current column is filled first

                rows_counter += 1

        return buttons_list


    def update_buttons(self, page: int=1) -> ButtonsList:
        """
        Updates the buttons list if the menu changes pages.

        The page number must be between 1 and the max values for the pages.
        """

        if 1 > page or self.max_pages < page:

            raise Exception(f"Page number is {page}. It must be between 1 and {self.max_pages} inclusive.") 

        buttons_list = list()

        for i in range((page - 1) * self.max_columns * self.max_rows, page * self.max_columns * self.max_rows):

            if i < len(self.buttons):

                buttons_list.append(self.buttons[i])

        if self.current_page < self.max_pages:

            buttons_list.append(self.pgdn_button)
        
        if self.current_page > 1:

            buttons_list.append(self.pgup_button)

        if self.parent: # add return button only if it is the main menu or a sub menu

            buttons_list.append(self.return_button)

        return buttons_list


    def change_page(self, to_next: bool=True, forced: bool=False) -> None:
        """
        Changes the current page to the previous or next one, depending of the parameter 'to_next'.
        If the new page is outside of the number of pages, does nothing if 'forced' is False, otherwise it rotates between the pages.
        """
        if forced:

            new_page = (self.max_pages % self.current_page) + 1

        else:

            new_page = (self.current_page + 1 if to_next else self.current_page - 1)
        
        if 1 <= new_page <= self.max_pages:

            self.current_page = new_page
            self.buttons_on_screen = self.update_buttons(new_page)


    def change_buttons(self, new_button_titles: StrList) -> None:
        """
        Changes all the buttons in the Menu.
        """

        self.buttons = self.generate_buttons(new_button_titles)


class Timer:
    """
    Class for a simple timer that counts
    from a certain number to 0.
    """

    def __init__(self, init_time: int, message: str='') -> None:
        """
        Initializes an instance of type 'Timer'.
        """

        self.initial_time = init_time
        self.current_time = init_time
        self.msg = message


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return f"Initial Time: {self.initial_time} - Current Time: {self.current_time}{f' - Message: {self.msg}' if self.msg != '' else ''}"


    def deduct(self, how_much: int) -> None:
        """
        Descends the countdown subtracting 'how_much' time from 'self.current_time'.
        """

        self.current_time -= how_much


    def reset(self) -> None:
        """
        Resets the timer to its original value ('self.initial_value').
        """

        self.current_time = self.initial_time
        self.msg = ''


    def is_zero_or_less(self) -> bool:
        """
        Returns 'True' if the current time of the Timer reaches zero (0) or further, and 'False' otherwise.
        """

        return self.current_time <= 0


    def change_message(self, new_message: str) -> None:
        """
        Changes the current message to a given new one.
        """

        self.msg = new_message

class SpringTimer:
    """
    Simple timer that oscillates between
    given 'floor' and 'ceiling' values.
    """

    def __init__(self, floor: int, ceiling: int, where_to_start: int, is_it_adding: bool=True) -> None:
        """
        Initializes an instance of type 'SpringTimer'.
        """
        
        if floor >= ceiling:

            raise Exception("'floor' parameter must NOT be greater or equal than 'ceiling'")

        if where_to_start < floor or where_to_start > ceiling:

            raise Exception(f"'where_to_start' parameter needs to be between {floor} and {ceiling} inclusive")

        self.floor = floor
        self.ceil = ceiling
        self.current = where_to_start
        self.adding = is_it_adding


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return f"Current: {self.current} - Floor: {self.floor} - Ceiling: {self.ceil} - Is it adding: {self.adding}"


    def count(self, how_much: int=1) -> None:
        """
        Advances the counting of the Timer, deducting if 'self.adding' is False, otherwise adding.
        """

        if self.adding:

            if self.current < self.ceil:

                self.current += how_much 
        else:

            if self.current > self.floor:

                self.current -= how_much

        if any((self.current <= self.floor, self.current >= self.ceil)):

            self.adding = not self.adding
