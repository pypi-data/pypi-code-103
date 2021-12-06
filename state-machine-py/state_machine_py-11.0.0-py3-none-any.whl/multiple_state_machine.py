
import queue

from state_machine_py.intermachine import Intermachine
from state_machine_py.state_machine import StateMachine


class MultipleStateMachine():

    def __init__(self):
        self._machines = {}

    @property
    def machines(self):
        return self._machines

    def create_machine(self, machine_key, context, state_creator_dict, transition_dict):
        """マルチプルステートマシンに紐づいているステートマシンを生成します"""
        machine = StateMachine(
            context=context,
            state_creator_dict=state_creator_dict,
            transition_dict=transition_dict,
            intermachine=Intermachine(self, machine_key),
            name=machine_key)

        self._machines[machine_key] = machine
        return machine
