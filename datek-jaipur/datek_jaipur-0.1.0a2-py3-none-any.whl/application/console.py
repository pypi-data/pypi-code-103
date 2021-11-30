from asyncio import run

from datek_jaipur.application.adapters.console.adapter import ConsoleAdapter
from datek_jaipur.application.state_machine.fsm import FSM
from datek_jaipur.application.state_machine.scope import Scope
from datek_jaipur.application.state_machine.states import (
    Start,
    PlayerTurn,
    End,
    PlayerWon,
)


def create_fsm() -> FSM:
    scope = Scope(adapter_class=ConsoleAdapter)
    return FSM([Start, PlayerTurn, PlayerWon, End], scope=scope)


def main():
    fsm = create_fsm()
    try:
        run(fsm.run())
    except KeyboardInterrupt:
        pass
