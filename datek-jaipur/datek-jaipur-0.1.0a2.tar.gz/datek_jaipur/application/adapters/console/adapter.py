from typing import Type

from datek_jaipur.application.adapters.base import BaseAdapter
from datek_jaipur.application.adapters.console.constants import (
    TurnType,
    ConsoleGoodsType,
    PlayAgainAnswer,
    turn_prompt,
)
from datek_jaipur.application.adapters.console.errors import (
    InvalidTurnTypeError,
    InvalidAnswerError,
)
from datek_jaipur.application.adapters.console.formatters import (
    format_card_set,
    format_player,
    clear_screen,
    print_new_turn,
    format_error,
)
from datek_jaipur.application.state_machine.states import Start, End, PlayerTurn
from datek_jaipur.domain.compound_types.game import Game
from datek_jaipur.domain.events.game_created import GameCreated
from datek_jaipur.domain.events.goods_traded import GoodsTraded
from datek_jaipur.utils import run_in_thread_pool, BaseEvent


class ConsoleAdapter(BaseAdapter):
    _event_type: Type[BaseEvent]
    _prompt: str

    async def collect_data(self):
        print_new_turn()

        if self._state_class is Start:
            collect_method = _collect_data_for_start
        elif self._state_class is PlayerTurn:
            collect_method = self._collect_data_for_turn
        else:
            collect_method = self._collect_data_for_game_end

        try:
            result = await collect_method()
        except Exception as error:
            print(format_error(error))
            raise

        clear_screen()
        return result

    async def _collect_data_for_turn(self):
        current_player = self._game.current_player
        print(
            f"{format_player(current_player)}, it's your turn\n\n"
            f"Your score is: {current_player.score}\n"
            f"Your cards are: {format_card_set(current_player.goods)}\n"
            f"Your herd size is: {len(current_player.herd)}\n"
            f"Cards on deck: {format_card_set(self._game.cards_on_deck)}\n\n"
        )

        choice: str = await run_in_thread_pool(
            input, "Pick your action: (S)ell, (B)uy, (T)rade: "
        )
        print()

        try:
            turn_type: TurnType = TurnType(choice)
        except ValueError:
            raise InvalidTurnTypeError

        self._event_type = turn_type.value

        if turn_type == turn_type.T:
            return await self._handle_trade()

        prompt = turn_prompt[turn_type]

        choice: str = await run_in_thread_pool(input, prompt)
        choice = choice.strip()

        try:
            goods_type = ConsoleGoodsType(choice).value
        except ValueError:
            raise InvalidAnswerError

        event_params = {
            "game": self._game,
            "goods_type": goods_type,
        }

        event = self._event_type(**event_params)
        await event.apply()
        return event.result

    async def _collect_data_for_game_end(self):
        print(
            f"The winner is: {format_player(self._game.winner)} with score {self._game.winner.score}"
        )
        again = await run_in_thread_pool(input, "Would you like to play again (y/n)? ")
        try:
            answer = PlayAgainAnswer(again)
        except ValueError:
            raise InvalidAnswerError
        return Start if answer == PlayAgainAnswer.Y else End

    async def _handle_trade(self):
        goods_to_acquire_str: str = await run_in_thread_pool(
            input, "Pick the cards you want to have: "
        )
        goods_to_acquire_str = goods_to_acquire_str.strip()

        goods_to_throw_str: str = await run_in_thread_pool(
            input, "Pick the cards you want to throw away: "
        )
        goods_to_throw_str = goods_to_throw_str.strip()

        try:
            goods_to_throw = tuple(
                ConsoleGoodsType(choice.strip()).value
                for choice in goods_to_throw_str.split(" ")
            )

            goods_to_acquire = tuple(
                ConsoleGoodsType(choice.strip()).value
                for choice in goods_to_acquire_str.split(" ")
            )
        except ValueError:
            raise InvalidAnswerError

        event = GoodsTraded(
            game=self._game,
            goods_to_give_away=goods_to_throw,
            goods_to_acquire=goods_to_acquire,
        )

        await event.apply()
        return event.result


async def _collect_data_for_start():
    player1_name = await run_in_thread_pool(input, "Enter player 1 name: ")
    player2_name = await run_in_thread_pool(input, "Enter player 2 name: ")

    event = GameCreated(
        player1_name=player1_name,
        player2_name=player2_name,
    )

    await event.apply()
    return event.result
