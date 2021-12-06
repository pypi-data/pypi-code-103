"""
Main Module. It encases all the other modules to start the game.
"""

from . import gamelib, graphics, game_state, game_controls, files
from .consts import PLAYER_SPRITE, WIDTH, HEIGHT


def main() -> None:
    """
    Main function. Initializes the game.
    """

    gamelib.title(f"Star Slayer - Alpha")
    gamelib.resize(WIDTH, HEIGHT)
    gamelib.icon(PLAYER_SPRITE)

    game = game_state.Game(inital_power=3)
    controls = game_controls.GameControls()

    keys_pressed = dict()
    events_processed = dict()

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

            elif event.type == gamelib.EventType.KeyRelease:

                keys_pressed[event.key] = False

            elif event.type == gamelib.EventType.ButtonPress:

                if event.mouse_button == 1:

                    controls.process_click(event.x, event.y, game)

        for key in keys_pressed:

            action = controls.process_key(key)

            if keys_pressed.get(key, False):

                events_processed[action] = True

            elif all((not keys_pressed.get(repeated_key, False) for repeated_key in files.list_repeated_keys(action))):

                events_processed[action] = False

        for game_action in events_processed:

            if events_processed.get(game_action, False): controls.process_action(game_action, game)

        if controls.is_on_prompt:

            if is_first_lap:

                is_first_lap = False
            
            else:

                is_first_lap = True
                controls.prompt(game)

        game.advance_game()
        controls.refresh(keys_pressed)

if __name__ == "__main__":

    gamelib.init(main)