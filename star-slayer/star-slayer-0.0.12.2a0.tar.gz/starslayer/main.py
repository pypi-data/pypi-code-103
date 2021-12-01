"""
Main Module. It encases all the other modules to start the game.
"""

from . import gamelib, graphics, game_state, game_controls
from .consts import PLAYER_SPRITE, WIDTH, HEIGHT


def main() -> None:
    """
    Main function. Initializes the game.
    """

    gamelib.title(f"Star Slayer (Pre)")
    gamelib.resize(WIDTH, HEIGHT)
    gamelib.icon(PLAYER_SPRITE)

    game = game_state.Game(inital_power=3)
    controls = game_controls.GameControls()

    keys_pressed = dict()

    is_first_lap = True # So that some actions take place in the next iteration of the loop

    while gamelib.loop(fps=60):

        if controls.exit:
            break

        gamelib.draw_begin()
        graphics.draw_screen(game, controls)
        gamelib.draw_end()

        for event in gamelib.get_events():

            if not event:  
                break

            if event.type == gamelib.EventType.KeyPress:

                keys_pressed[event.key] = True

            if event.type == gamelib.EventType.KeyRelease:

                keys_pressed[event.key] = False

            if event.type == gamelib.EventType.ButtonPress:

                if event.mouse_button == 1:

                    controls.process_click(event.x, event.y, game)

        for key in keys_pressed:

            if keys_pressed.get(key, False): controls.process_action(controls.process_key(key), game)

        if controls.is_changing_key:

            if is_first_lap:

                is_first_lap = False
            
            else:

                is_first_lap = True
                controls.add_key(game.action_to_show, game)

        game.advance_game()
        controls.refresh(keys_pressed)

if __name__ == "__main__":

    gamelib.init(main)