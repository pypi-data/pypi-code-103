"""state-machine certainty algorithms"""
from state_machine import State, Event, acts_as_state_machine, after, InvalidStateTransition
from typing import Union, Callable
from time import perf_counter


# noinspection PyCompatibility
@acts_as_state_machine
class CertaintySelection:

    """implement the state-machine for certainty logic"""

    # defined states
    length = State(initial=True)
    processed = State()

    # defined events
    converted = Event(from_states=length, to_state=processed)

    def __init__(self, scale_index: dict, distance: Union[float, int], algorithm: Callable):
        self.scale = scale_index
        # noinspection PyTypeChecker
        self.index: list = list(self.scale.keys())
        self.distance = distance
        # self.stack = []  LifoQueue(maxsize=5)
        self.confidence: float = 0.0
        self.algorithm = algorithm

    @after('converted')
    def length_conv(self):

        """get the confidence for a given distance on the index/scale"""
        self.confidence = self.algorithm(self.scale, self.index, self.distance)


def state_controller(scale: dict, distance: Union[float, int], algorithm: Callable):
    """controls the states"""

    # create state-machine object
    state_mach = CertaintySelection(scale, distance, algorithm)

    # control state transitioning
    try:
        # noinspection PyCallingNonCallable
        state_mach.converted()
        return state_mach.confidence
    except InvalidStateTransition or TypeError:
        raise BrokenPipeError


"""scale = {0.0: 1.0, 1.0: 1.0, 10.0: 0.9, 100.0: 0.8, 250.0: 0.7, 1000.0: 0.6, 1000.99: 0.5}
start = perf_counter()
print(state_controller(scale, 101))
print(perf_counter() - start)"""


# ------------------------- TEST FUNCTIONS ---------------------------

# noinspection PyCompatibility
def test1(distance, confidence=0.0):

    """get the confidence for a given distance on the index/scale"""

    # set boolean flag
    flag: bool = False

    # define array length
    length = len(index)

    # run iteration over conditional array options
    while flag is False:
        for i in range(1, length - 1):
            if index[i - 1] < distance < index[i + 1]:
                confidence = confidence_index[index[i]]
                flag = True
            else:
                continue

        if not flag:
            print("in not flag")
            if distance > index[-1]:
                confidence = confidence_index[index[-1]]
                flag = True
            else:
                confidence = confidence_index[index[0]]
                flag = True

    return confidence


def test2(distance, confidence=0.0):
    stack = []
    for i in range(1, len(index2)):
        if distance > index2[i-1]:
            stack.append(confidence_index2[index2[i]])
        else:
            continue

    # print(stack)
    try:
        return stack.pop()
    except IndexError:
        return confidence_index2[index2[-1]]
