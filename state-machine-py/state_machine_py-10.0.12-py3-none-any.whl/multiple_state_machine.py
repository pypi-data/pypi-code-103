
import queue

from state_machine_py.intermachine import Intermachine
from state_machine_py.state_machine import StateMachine


class MultipleStateMachine():

    def __init__(self):
        self._machines = {}
        self._input_queues = {}

    @property
    def machines(self):
        return self._machines

    @property
    def input_queues(self):
        return self._input_queues

    def create_machine(self, machine_key, context, state_creator_dict, transition_dict):
        """マルチプルステートマシンに紐づいているステートマシンを生成します"""
        machine = StateMachine(
            context=context,
            state_creator_dict=state_creator_dict,
            transition_dict=transition_dict,
            intermachine=Intermachine(self, machine_key),
            name=machine_key)

        self._machines[machine_key] = machine
        self._input_queues[machine_key] = queue.Queue()
        return machine
