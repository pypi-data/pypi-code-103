"""
Graphics Module. Draws anything that the player
sees on screen.
"""

from . import gamelib, files
from .game_state import Game
from .game_controls import GameControls as Controls
from .utils import Menu
from .characters import Ship
from .consts import DEBUG_TEXT, PROFILES_DELETER, PROFILES_TITLE, WIDTH, HEIGHT, GUI_SPACE, DEBUG_LINES, PROFILES_CHANGER, SPECIAL_CHARS, GAME_TITLE, OPTIONS_TITLE, CONTROLS_TITLE


def get_color(game: Game, name: str) -> str:
    """
    Wrapper for searching colors in game profile.
    """

    return game.color_profile.get(name)


def draw_background(game: Game) -> None:
    """
    Draws the background of the game (duh).
    """

    gamelib.draw_rectangle(0, 0, WIDTH, HEIGHT, fill=get_color(game, "BG_COLOR"))


def draw_GUI(game: Game) -> None:
    """
    Draws the User Interface.
    """

    aux_cons = (HEIGHT // 70)

    gamelib.draw_rectangle(WIDTH - GUI_SPACE, 0, WIDTH, HEIGHT, outline=get_color(game, "GUI_OUTLINE_1"), fill=get_color(game, "GUI_COLOR_1"))

    gamelib.draw_text(f"Time: {game.level_timer.current_time}", (WIDTH - GUI_SPACE) + aux_cons, aux_cons, fill=get_color(game, "TEXT_COLOR_1"), anchor="nw")

    # Power Level
    gamelib.draw_text("Current Power Level:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.73, size=(WIDTH // 50), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text(f"{game.power_level}", WIDTH - aux_cons, HEIGHT * 0.73, size=(WIDTH // 50), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    gamelib.draw_line(WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.765, WIDTH - aux_cons, HEIGHT * 0.765, width=(aux_cons // 2), fill=get_color(game, "GUI_COLOR_2"))

    # Hardness
    gamelib.draw_text("Current Hardness:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.8, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text(f"{game.player.hardness}", WIDTH - aux_cons, HEIGHT * 0.8, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    # Speed
    gamelib.draw_text("Current Speed:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.85, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text(f"{game.player.speed}", WIDTH - aux_cons, HEIGHT * 0.85, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    # Health
    gamelib.draw_text("Remaining health:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.9, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text(f"{game.player.hp}  /  {game.player.max_hp}", WIDTH - aux_cons, HEIGHT * 0.9, size=(WIDTH // 62), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    # Health Bar
    gamelib.draw_rectangle(WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.93, WIDTH - aux_cons, HEIGHT - aux_cons, width=(aux_cons // 2), outline=get_color(game, "GUI_OUTLINE_2"), fill=get_color(game, "GUI_OUTLINE_1"))

    if not game.player.has_no_health():

        hp_percentage = (game.player.hp / game.player.max_hp) * 100

        bar_start = WIDTH - GUI_SPACE + (2 * aux_cons)
        bar_end = WIDTH - (2 * aux_cons)

        augment = ((bar_end - bar_start) / 100) * hp_percentage

        gamelib.draw_rectangle(bar_start, HEIGHT * 0.945, bar_start + augment, HEIGHT - (2 * aux_cons), outline=get_color(game, "GUI_OUTLINE_1"), fill=get_color(game, "GUI_COLOR_3"))


def draw_menus(game: Game, controls: Controls) -> None:
    """
    Draws in the screen the current selected menu.
    """

    menu = game.current_menu

    draw_menu_buttons(game, menu)

    if menu is game.main_menu:

        gamelib.draw_text(GAME_TITLE, WIDTH // 2, HEIGHT // 4, size=(WIDTH // 90), fill=get_color(game, "TEXT_COLOR_1"), justify='c')

    elif menu is game.options_menu:

        gamelib.draw_text(OPTIONS_TITLE, WIDTH // 2, HEIGHT // 4, size=(WIDTH // 90), fill=get_color(game, "TEXT_COLOR_1"), justify='c')

    elif menu is game.controls_menu:

        gamelib.draw_text(CONTROLS_TITLE, int(WIDTH * 0.130666), (HEIGHT // 15), size=(HEIGHT // 235), fill=get_color(game, "TEXT_COLOR_1"), justify='c')
        draw_changeable_buttons(game, controls)

    elif menu is game.profiles_menu:

        gamelib.draw_text(PROFILES_TITLE, int(WIDTH * 0.893333), (HEIGHT // 15), size=(HEIGHT // 235), fill=get_color(game, "TEXT_COLOR_1"), justify='c')
        draw_profile_attributes(game, controls)


def draw_changeable_buttons(game: Game, controls: Controls) -> None:
    """
    Draws the information of the action and its assigned keys.
    If possible, it also allows it to edit said information.
    """

    aux_cons = (HEIGHT // 70)

    gamelib.draw_rectangle((WIDTH // 4) + aux_cons, aux_cons, WIDTH - aux_cons, HEIGHT - aux_cons, width=(HEIGHT // 87), outline=get_color(game, "MENU_OUTLINE_1"), fill=get_color(game, "MENU_COLOR_1"))
    gamelib.draw_text(f"{game.action_to_show}", int(WIDTH * (5 / 8)), (HEIGHT // 8), fill=get_color(game, "TEXT_COLOR_1"), size=(WIDTH // 10), justify='c')

    keys_assigned = files.list_repeated_keys(game.action_to_show, files.map_keys())

    if '/' in keys_assigned: keys_assigned.remove('/')

    if not keys_assigned:

        gamelib.draw_text(f"Action is currently not binded to any key", (WIDTH * (5 / 8)), (HEIGHT / 3.5), fill=get_color(game, "TEXT_COLOR_1"), size=(WIDTH // 34), justify='c')

    else:

        gamelib.draw_text(' - '.join(keys_assigned),
                        int(WIDTH * (5 / 8)), int(HEIGHT / 2.5), fill=get_color(game, "TEXT_COLOR_1"), size=(HEIGHT // 20), justify='c')

        gamelib.draw_text(f"Action is currently bound to the key{'s' if len(keys_assigned) > 1 else ''}", (WIDTH * (5 / 8)), (HEIGHT / 3.5), fill=get_color(game, "TEXT_COLOR_1"), size=(WIDTH // 34), justify='c')

    draw_menu_buttons(game, game.sub_menu)

    if controls.is_on_prompt:

        draw_key_changing_prompt(game)


def draw_key_changing_prompt(game: Game) -> None:
    """
    It draws a prompt in the screen that warns the player that a key is
    being changed and they need to press any key to try to bind it.
    """

    aux_cons = (HEIGHT // 10)

    gamelib.draw_rectangle(aux_cons, (HEIGHT // 2) - aux_cons, WIDTH - aux_cons, (HEIGHT // 2) + aux_cons, width=(HEIGHT // 90), outline=get_color(game, "MENU_OUTLINE_1"), fill=get_color(game, "MENU_COLOR_1"))
    gamelib.draw_text(f"Press any key to bind it to '{game.action_to_show}'", (WIDTH // 2), (HEIGHT // 2), fill=get_color(game, "TEXT_COLOR_1"), size=(HEIGHT // 30), justify='c')


def draw_profile_attributes(game: Game, controls: Controls) -> None:
    """
    Shows the user the current values for each attributes of a
    selected color profile.
    If possible, they can also edit such values.
    """

    draw_menu_buttons(game, game.sub_menu)

    for button in game.sub_menu.buttons_on_screen:

        if button.msg in SPECIAL_CHARS:

            continue

        width_extra = (button.width // 30)
        height_extra = (button.height // 4)

        oval_x = (button.width // 30)
        oval_y = (button.height // 30)

        x1 = button.x2 - width_extra * 5
        y1 = button.y1 + height_extra
        x2 = button.x2 - width_extra
        y2 = button.y2 - height_extra

        button_color = game.color_profile.get(button.msg, None)
        button_outline = get_color(game, "TEXT_COLOR_1")

        if button.msg not in [PROFILES_CHANGER, PROFILES_DELETER]:

            if button_color == '':

                gamelib.draw_line(x2 - oval_x,
                                y1 + oval_y,
                                x1 + oval_x,
                                y2 - oval_y,
                                fill=button_outline, width=2)

            gamelib.draw_oval(x1, y1, x2, y2,
                            outline=button_outline,
                            fill=button_color)

    if controls.is_on_prompt:

        draw_attribute_prompt(game)


def draw_attribute_prompt(game: Game) -> None:
    """
    Draws a prompt that asks the user to select a new color value
    for the attribute selected.
    """

    ...


def draw_menu_buttons(game: Game, menu: Menu) -> None:
    """
    Draws all the buttons of a given menu.
    """

    for button in menu.buttons_on_screen:

        gamelib.draw_rectangle(button.x1, button.y1, button.x2, button.y2,
                               width=((button.y2 - button.y1) // 25),
                               outline=get_color(game, "TEXT_COLOR_1"),
                               fill=get_color(game, "BUTTON_COLOR_1"),
                               activefill=get_color(game, "BUTTON_COLOR_2"))

        if button.msg:

            x_coord, y_coord = button.center
            btn_anchor = menu.button_anchor

            if button.msg in SPECIAL_CHARS or button.msg in [PROFILES_CHANGER, PROFILES_DELETER]:
            
                btn_anchor = 'c'

            else:

                if menu.button_anchor == 'c':

                    x_coord += menu.offset_x
                    y_coord += menu.offset_y

                else:

                    width_extra = (button.width // 50)
                    height_extra = (button.height // 50)

                    if 'n' in menu.button_anchor:

                        y_coord = button.y1 + height_extra

                    elif 's' in menu.button_anchor:

                        y_coord = button.y2 - height_extra

                    if 'w' in menu.button_anchor:

                        x_coord = button.x1 + width_extra

                    elif 'e' in menu.button_anchor:

                        x_coord = button.x2 - width_extra

            gamelib.draw_text(' '.join(button.msg.split('_')),
                              x_coord, y_coord,
                              size=int((button.y2 - button.y1) // (2 if button.msg in SPECIAL_CHARS else 4)),
                              fill=get_color(game, "TEXT_COLOR_1"),
                              anchor=btn_anchor,
                              justify='c')


def draw_ship(game: Game, ship: Ship, which_one: int=0) -> None:
    """
    Draws the sprite of a ship.

    'which_one' refers to which frame to draw.
    """

    if ship.sprites == None:

        gamelib.draw_rectangle(ship.x1, ship.y1, ship.x2, ship.y2, fill=get_color(game, "DEBUG_LINES_1"))

    else:

        gamelib.draw_image(ship.sprites[which_one], ship.x1, ship.y1)


def draw_bullets(game: Game) -> None:
    """
    Draws every single bullet currently on screen.
    """

    bullets = game.bullets

    for bullet in bullets:

        gamelib.draw_oval(bullet.x1, bullet.y1, bullet.x2, bullet.y2, outline=get_color(game, "GUI_OUTLINE_1"), fill=get_color(game, "TEXT_COLOR_1"))


def draw_debug_info(game: Game) -> None:
    """
    Draws debug information about the current game.
    """

    if game.show_debug_info:

        player = game.player
        cx, cy = player.center
        debug_cons = (HEIGHT // 70)

        debug_text = DEBUG_TEXT.format(player_x1=player.x1,
                                       player_y1=player.y1,
                                       player_x2=player.x2,
                                       player_y2=player.y2,

                                       hitbox_center=f"({cx}, {cy})",
                                       shooting_cooldown=("Ready!" if game.shooting_cooldown.is_zero_or_less() else game.shooting_cooldown.current_time),
                                       inv_cooldown=("Ready!" if game.invulnerability.is_zero_or_less() else game.invulnerability.current_time),

                                       power_level=game.power_level,

                                       health=game.player.hp,
                                       hardness=game.player.hardness,
                                       speed=game.player.speed,

                                       enemies=len(game.enemies),
                                       bullets=len(game.bullets))

        gamelib.draw_text(debug_text, debug_cons, debug_cons, size=debug_cons, fill=get_color(game, "TEXT_COLOR_1"), anchor="nw")

        if DEBUG_LINES:

            draw_debug_lines(game)

            for bullet in game.bullets:

                x, y = bullet.center
                gamelib.draw_line(x, y - 30, x, y + 30, fill=get_color(game, "DEBUG_LINES_2"))
                gamelib.draw_line(x - 30, y, x + 30, y, fill=get_color(game, "DEBUG_LINES_2"))

            for enem in game.enemies:

                x, y = enem.center
                gamelib.draw_line(x, y - 50, x, y + 50, fill=get_color(game, "DEBUG_LINES_2"))
                gamelib.draw_line(x - 50, y, x + 50, y, fill=get_color(game, "DEBUG_LINES_2"))


def draw_debug_lines(game: Game) -> None:
    """
    Marks the limit of hitboxes and additional debug info through lines.
    """

    player = game.player
    cx, cy = player.center

    # Upper Lines
    gamelib.draw_line(cx, 0, cx, player.y1, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(cx - 5, player.y1, cx + 5, player.y1, fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom Lines
    gamelib.draw_line(cx, player.y2, cx, HEIGHT, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(cx - 5, player.y2, cx + 5, player.y2, fill=get_color(game, "DEBUG_LINES_1"))

    # Left Lines
    gamelib.draw_line(0, cy, player.x1, cy, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x1, cy - 5, player.x1, cy + 5, fill=get_color(game, "DEBUG_LINES_1"))

    # Right Lines
    gamelib.draw_line(player.x2, cy, WIDTH, cy, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x2, cy - 5, player.x2, cy + 5, fill=get_color(game, "DEBUG_LINES_1"))


    # Upper-Left Corner
    gamelib.draw_line(player.x1, player.y1, player.x1 + 10, player.y1, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x1, player.y1, player.x1, player.y1 + 10, fill=get_color(game, "DEBUG_LINES_1"))

    # Upper-Right Corner
    gamelib.draw_line(player.x2, player.y1, player.x2 - 10, player.y1, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x2, player.y1, player.x2, player.y1 + 10, fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom-Left Corner
    gamelib.draw_line(player.x1, player.y2, player.x1 + 10, player.y2, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x1, player.y2, player.x1, player.y2 - 10, fill=get_color(game, "DEBUG_LINES_1"))

    # Bottom-Right Corner
    gamelib.draw_line(player.x2, player.y2, player.x2 - 10, player.y2, fill=get_color(game, "DEBUG_LINES_1"))
    gamelib.draw_line(player.x2, player.y2, player.x2, player.y2 - 10, fill=get_color(game, "DEBUG_LINES_1"))


def draw_about(game: Game) -> None:
    """
    Shows the information about the people involved in this game.
    """

    aux_cons = (WIDTH // 10)

    gamelib.draw_rectangle(0, 0, WIDTH, HEIGHT, width=(HEIGHT // 87), outline=get_color(game, "ABOUT_OUTLINE_1"), fill=get_color(game, "ABOUT_COLOR_1"))

    gamelib.draw_text("SO, ABOUT\nTHIS GAME...", (WIDTH // 2), (HEIGHT // 6), size=(HEIGHT // 12), fill=get_color(game, "TEXT_COLOR_1"), justify='c')

    # Pixel-Art
    gamelib.draw_text("Pixel-Art:", aux_cons, HEIGHT * 0.4, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text("Franco 'NLGS' Lighterman", WIDTH - aux_cons, HEIGHT * 0.4, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    # Coding
    gamelib.draw_text("Coding:", aux_cons, HEIGHT * 0.6, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text("Franco 'NLGS' Lighterman", WIDTH - aux_cons, HEIGHT * 0.6, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    # Gamelib
    gamelib.draw_text("Gamelib Library:", aux_cons, HEIGHT * 0.8, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='w')
    gamelib.draw_text("Diego Essaya", WIDTH - aux_cons, HEIGHT * 0.8, size=(HEIGHT // 30), fill=get_color(game, "TEXT_COLOR_1"), anchor='e')

    gamelib.draw_text("Press 'RETURN' to return", (WIDTH // 2), HEIGHT - 20, size=(HEIGHT // 50), fill=get_color(game, "TEXT_COLOR_1"), justify='c')


def draw_exiting_bar(game: Game, controls: Controls) -> None:
    """
    Draws a mini-bar that shows how much time is left until it exits the game.
    """
    aux_cons = (HEIGHT // 60)

    gamelib.draw_rectangle(aux_cons, aux_cons, (10 * aux_cons), (3 * aux_cons), width=(aux_cons // 3), outline=get_color(game, "TEXT_COLOR_1"), fill=get_color(game, "GUI_OUTLINE_1"))

    percentage = 100 - ((controls.exiting_cooldown.current_time / controls.exiting_cooldown.initial_time) * 100)

    bar_start = (1.5 * aux_cons)
    bar_end = (9.5 * aux_cons)

    augment = ((bar_end - bar_start) / 100) * percentage

    gamelib.draw_rectangle(bar_start, (1.5 * aux_cons), bar_start + augment, (2.5 * aux_cons), outline=get_color(game, "GUI_OUTLINE_1"), fill=get_color(game, "TEXT_COLOR_1"))

    gamelib.draw_text("Exiting Game...", (5.5 * aux_cons), (4.5 * aux_cons), size=aux_cons, anchor='c')


def draw_screen(game: Game, controls: Controls) -> None:
    """
    Draws the entirety of the elements on the screen.
    """
    draw_background(game)
    draw_bullets(game)
    draw_debug_info(game)

    if game.is_in_game:

        draw_ship(game, game.player, (0 if game.invulnerability.is_zero_or_less() else 1))

        for enem in game.enemies:

            draw_ship(game, enem)

        draw_GUI(game)

    elif controls.show_about:

        draw_about(game)

    else:

        draw_menus(game, controls)

    if controls.exiting:

        draw_exiting_bar(game, controls)
