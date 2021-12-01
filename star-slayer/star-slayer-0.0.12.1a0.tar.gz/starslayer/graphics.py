"""
Graphics Module. Draws anything that the player
sees on screen.
"""

from . import gamelib, files
from .game_state import Game
from .game_controls import GameControls as Controls
from .objects import Menu, Ship
from .consts import DEBUG_TEXT, WIDTH, HEIGHT, GUI_SPACE, DEBUG_LINES, SPECIAL_CHARS, GAME_TITLE, OPTIONS_TITLE, CONTROLS_TITLE


def draw_background(controls: Controls) -> None:
    """
    Draws the background of the game (duh).
    """

    gamelib.draw_rectangle(0, 0, WIDTH, HEIGHT, fill=controls.color_profile["BG_COLOR"])


def draw_GUI(game: Game, controls: Controls) -> None:
    """
    Draws the User Interface.
    """

    aux_cons = (HEIGHT // 70)

    gamelib.draw_rectangle(WIDTH - GUI_SPACE, 0, WIDTH, HEIGHT, outline=controls.color_profile["GUI_OUTLINE_1"], fill=controls.color_profile["GUI_COLOR_1"])

    gamelib.draw_text(f"Time: {game.level_timer.current_time}", (WIDTH - GUI_SPACE) + aux_cons, aux_cons, fill=controls.color_profile["TEXT_COLOR_1"], anchor="nw")

    # Power Level
    gamelib.draw_text("Current Power Level:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.73, size=(WIDTH // 50), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text(f"{game.power_level}", WIDTH - aux_cons, HEIGHT * 0.73, size=(WIDTH // 50), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    gamelib.draw_line(WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.765, WIDTH - aux_cons, HEIGHT * 0.765, width=(aux_cons // 2), fill=controls.color_profile["GUI_COLOR_2"])

    # Hardness
    gamelib.draw_text("Current Hardness:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.8, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text(f"{game.player.hardness}", WIDTH - aux_cons, HEIGHT * 0.8, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    # Speed
    gamelib.draw_text("Current Speed:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.85, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text(f"{game.player.speed}", WIDTH - aux_cons, HEIGHT * 0.85, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    # Health
    gamelib.draw_text("Remaining health:", WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.9, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text(f"{game.player.hp}  /  {game.player.max_hp}", WIDTH - aux_cons, HEIGHT * 0.9, size=(WIDTH // 62), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    # Health Bar
    gamelib.draw_rectangle(WIDTH - GUI_SPACE + aux_cons, HEIGHT * 0.93, WIDTH - aux_cons, HEIGHT - aux_cons, width=(aux_cons // 2), outline=controls.color_profile["GUI_OUTLINE_2"], fill=controls.color_profile["GUI_OUTLINE_1"])

    if not game.player.has_no_health():

        hp_percentage = (game.player.hp / game.player.max_hp) * 100

        bar_start = WIDTH - GUI_SPACE + (2 * aux_cons)
        bar_end = WIDTH - (2 * aux_cons)

        augment = ((bar_end - bar_start) / 100) * hp_percentage

        gamelib.draw_rectangle(bar_start, HEIGHT * 0.945, bar_start + augment, HEIGHT - (2 * aux_cons), outline=controls.color_profile["GUI_OUTLINE_1"], fill=controls.color_profile["GUI_COLOR_3"])


def draw_menus(game: Game, controls: Controls) -> None:
    """
    Draws in the screen the current selected menu.
    """

    menu = game.current_menu

    draw_menu_buttons(menu, controls)

    if menu is game.main_menu:

        gamelib.draw_text(GAME_TITLE, WIDTH // 2, HEIGHT // 4, size=(WIDTH // 90), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')

    elif menu is game.options_menu:

        gamelib.draw_text(OPTIONS_TITLE, WIDTH // 2, HEIGHT // 4, size=(WIDTH // 90), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')

    elif menu is game.controls_menu:

        gamelib.draw_text(CONTROLS_TITLE, (WIDTH // 8) + 5, (HEIGHT // 15), size=(HEIGHT // 235), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')
        draw_changeable_buttons(game, controls)


def draw_changeable_buttons(game: Game, controls: Controls) -> None:
    """
    Draws the information of the action and its assigned keys.
    If possible, it also allows it to edit said information.
    """

    aux_cons = (HEIGHT // 70)

    gamelib.draw_rectangle((WIDTH // 4) + aux_cons, aux_cons, WIDTH - aux_cons, HEIGHT - aux_cons, width=(HEIGHT // 87), outline=controls.color_profile["MENU_OUTLINE_1"], fill=controls.color_profile["MENU_COLOR_1"])
    gamelib.draw_text(f"{game.action_to_show}", (WIDTH * (5 / 8)), (HEIGHT // 8), fill=controls.color_profile["TEXT_COLOR_1"], size=(WIDTH // 10), justify='c')

    keys_assigned = files.list_repeated_keys(game.action_to_show, files.map_keys())

    if '/' in keys_assigned: keys_assigned.remove('/')

    if not keys_assigned:

        gamelib.draw_text(f"Action is currently not binded to any key", (WIDTH * (5 / 8)), (HEIGHT / 3.5), fill=controls.color_profile["TEXT_COLOR_1"], size=(WIDTH // 34), justify='c')

    else:

        gamelib.draw_text(' - '.join(keys_assigned),
                        (WIDTH * (5 / 8)), (HEIGHT / 2.5), fill=controls.color_profile["TEXT_COLOR_1"], size=(HEIGHT // 20), justify='c')

        gamelib.draw_text(f"Action is currently bound to the key{'s' if len(keys_assigned) > 1 else ''}", (WIDTH * (5 / 8)), (HEIGHT / 3.5), fill=controls.color_profile["TEXT_COLOR_1"], size=(WIDTH // 34), justify='c')

    draw_menu_buttons(game.sub_menu, controls)

    if controls.is_changing_key:

        draw_changing_prompt(game, controls)

def draw_changing_prompt(game: Game, controls: Controls) -> None:
    """
    It draws a prompt in the screen that warns the player that a key is
    being changed and they need to press any key to try to bind it.
    """

    aux_cons = (HEIGHT // 10)

    gamelib.draw_rectangle(aux_cons, (HEIGHT // 2) - aux_cons, WIDTH - aux_cons, (HEIGHT // 2) + aux_cons, width=(HEIGHT // 90), outline=controls.color_profile["MENU_OUTLINE_1"], fill=controls.color_profile["MENU_COLOR_1"])
    gamelib.draw_text(f"Press any key to bind it to '{game.action_to_show}'", (WIDTH // 2), (HEIGHT // 2), fill=controls.color_profile["TEXT_COLOR_1"], size=(HEIGHT // 30), justify='c')

def draw_menu_buttons(menu: Menu, controls: Controls) -> None:
    """
    Draws all the buttons of a given menu.
    """

    for button in menu.buttons_on_screen:

        gamelib.draw_rectangle(button.x1, button.y1, button.x2, button.y2, width=((button.y2 - button.y1) // 25), outline=controls.color_profile["TEXT_COLOR_1"],  fill=controls.color_profile["BUTTON_COLOR_1"], activefill=controls.color_profile["BUTTON_COLOR_2"])

        if button.msg:

            center_x, center_y = button.center()
            gamelib.draw_text(button.msg, center_x, center_y, size=((button.y2 - button.y1) // (2 if button.msg in SPECIAL_CHARS else 4)), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')

def draw_ship(controls: Controls, ship: Ship, which_one: int=0) -> None:
    """
    Draws the sprite of a ship.

    'which_one' refers to which frame to draw.
    """

    if ship.sprites == None:

        gamelib.draw_rectangle(ship.x1, ship.y1, ship.x2, ship.y2, fill=controls.color_profile["DEBUG_LINES_1"])

    else:

        gamelib.draw_image(ship.sprites[which_one], ship.x1, ship.y1)

def draw_bullets(game: Game, controls: Controls) -> None:
    """
    Draws every single bullet currently on screen.
    """

    bullets = game.bullets

    for bullet in bullets:

        gamelib.draw_oval(bullet.x1, bullet.y1, bullet.x2, bullet.y2, outline=controls.color_profile["GUI_OUTLINE_1"], fill=controls.color_profile["TEXT_COLOR_1"])

def draw_debug_info(game: Game, controls: Controls) -> None:
    """
    Draws debug information about the current game.
    """

    if game.show_debug_info:

        player = game.player
        cx, cy = player.center()
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

        gamelib.draw_text(debug_text, debug_cons, debug_cons, size=debug_cons, fill=controls.color_profile["TEXT_COLOR_1"], anchor="nw")

        if DEBUG_LINES:

            draw_debug_lines(game, controls)

            for bullet in game.bullets:

                x, y = bullet.center()
                gamelib.draw_line(x, y - 30, x, y + 30, fill=controls.color_profile["DEBUG_LINES_2"])
                gamelib.draw_line(x - 30, y, x + 30, y, fill=controls.color_profile["DEBUG_LINES_2"])

            for enem in game.enemies:

                x, y = enem.center()
                gamelib.draw_line(x, y - 50, x, y + 50, fill=controls.color_profile["DEBUG_LINES_2"])
                gamelib.draw_line(x - 50, y, x + 50, y, fill=controls.color_profile["DEBUG_LINES_2"])

def draw_debug_lines(game: Game, controls: Controls) -> None:
    """
    Marks the limit of hitboxes and additional debug info through lines.
    """

    player = game.player
    cx, cy = player.center()

    # Upper Lines
    gamelib.draw_line(cx, 0, cx, player.y1, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(cx - 5, player.y1, cx + 5, player.y1, fill=controls.color_profile["DEBUG_LINES_1"])

    # Bottom Lines
    gamelib.draw_line(cx, player.y2, cx, HEIGHT, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(cx - 5, player.y2, cx + 5, player.y2, fill=controls.color_profile["DEBUG_LINES_1"])

    # Left Lines
    gamelib.draw_line(0, cy, player.x1, cy, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x1, cy - 5, player.x1, cy + 5, fill=controls.color_profile["DEBUG_LINES_1"])

    # Right Lines
    gamelib.draw_line(player.x2, cy, WIDTH, cy, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x2, cy - 5, player.x2, cy + 5, fill=controls.color_profile["DEBUG_LINES_1"])


    # Upper-Left Corner
    gamelib.draw_line(player.x1, player.y1, player.x1 + 10, player.y1, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x1, player.y1, player.x1, player.y1 + 10, fill=controls.color_profile["DEBUG_LINES_1"])

    # Upper-Right Corner
    gamelib.draw_line(player.x2, player.y1, player.x2 - 10, player.y1, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x2, player.y1, player.x2, player.y1 + 10, fill=controls.color_profile["DEBUG_LINES_1"])

    # Bottom-Left Corner
    gamelib.draw_line(player.x1, player.y2, player.x1 + 10, player.y2, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x1, player.y2, player.x1, player.y2 - 10, fill=controls.color_profile["DEBUG_LINES_1"])

    # Bottom-Right Corner
    gamelib.draw_line(player.x2, player.y2, player.x2 - 10, player.y2, fill=controls.color_profile["DEBUG_LINES_1"])
    gamelib.draw_line(player.x2, player.y2, player.x2, player.y2 - 10, fill=controls.color_profile["DEBUG_LINES_1"])

def draw_about(controls: Controls) -> None:
    """
    Shows the information about the people involved in this game.
    """

    aux_cons = (WIDTH // 10)

    gamelib.draw_rectangle(0, 0, WIDTH, HEIGHT, width=(HEIGHT // 87), outline=controls.color_profile["ABOUT_OUTLINE_1"], fill=controls.color_profile["ABOUT_COLOR_1"])

    gamelib.draw_text("SO, ABOUT\nTHIS GAME...", (WIDTH // 2), (HEIGHT // 6), size=(HEIGHT // 12), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')

    # about_text = f"Pixel-Art:\t\t\tFranco 'NLGS' Lighterman\n\n\nCoding:\t\t\tFranco 'NLGS' Lighterman\n\n\nGamelib Library:\t\t\tDiego Essaya"

    # gamelib.draw_text(about_text, (HEIGHT // 14), (HEIGHT / 2.5), size=(HEIGHT // 40), anchor="nw")

    # Pixel-Art
    gamelib.draw_text("Pixel-Art:", aux_cons, HEIGHT * 0.4, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text("Franco 'NLGS' Lighterman", WIDTH - aux_cons, HEIGHT * 0.4, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    # Coding
    gamelib.draw_text("Coding:", aux_cons, HEIGHT * 0.6, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text("Franco 'NLGS' Lighterman", WIDTH - aux_cons, HEIGHT * 0.6, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    # Gamelib
    gamelib.draw_text("Gamelib Library:", aux_cons, HEIGHT * 0.8, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='w')
    gamelib.draw_text("Diego Essaya", WIDTH - aux_cons, HEIGHT * 0.8, size=(HEIGHT // 30), fill=controls.color_profile["TEXT_COLOR_1"], anchor='e')

    gamelib.draw_text("Press 'RETURN' to return", (WIDTH // 2), HEIGHT - 20, size=(HEIGHT // 50), fill=controls.color_profile["TEXT_COLOR_1"], justify='c')

def draw_exiting_bar(controls: Controls) -> None:
    """
    Draws a mini-bar that shows how much time is left until it exits the game.
    """
    aux_cons = (HEIGHT // 60)

    gamelib.draw_rectangle(aux_cons, aux_cons, (10 * aux_cons), (3 * aux_cons), width=(aux_cons // 3), outline=controls.color_profile["TEXT_COLOR_1"], fill=controls.color_profile["GUI_OUTLINE_1"])

    percentage = 100 - ((controls.exiting_cooldown.current_time / controls.exiting_cooldown.initial_time) * 100)

    bar_start = (1.5 * aux_cons)
    bar_end = (9.5 * aux_cons)

    augment = ((bar_end - bar_start) / 100) * percentage

    gamelib.draw_rectangle(bar_start, (1.5 * aux_cons), bar_start + augment, (2.5 * aux_cons), outline=controls.color_profile["GUI_OUTLINE_1"], fill=controls.color_profile["TEXT_COLOR_1"])

    gamelib.draw_text("Exiting Game...", (5.5 * aux_cons), (4.5 * aux_cons), size=aux_cons, anchor='c')

def draw_screen(game: Game, controls: Controls) -> None:
    """
    Draws the entirety of the elements on the screen.
    """
    draw_background(controls)
    draw_bullets(game, controls)
    draw_debug_info(game, controls)

    if game.is_in_game:

        draw_ship(controls, game.player, (0 if game.invulnerability.is_zero_or_less() else 1))

        for enem in game.enemies:

            draw_ship(controls, enem)

        draw_GUI(game, controls)

    elif controls.show_about:

        draw_about(controls)

    else:

        draw_menus(game, controls)

    if controls.exiting:

        draw_exiting_bar(controls)