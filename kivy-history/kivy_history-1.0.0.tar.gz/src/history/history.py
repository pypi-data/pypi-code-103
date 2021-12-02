import os

from kivy.event import EventDispatcher
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty, BoundedNumericProperty, ObjectProperty
# from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManagerException

from .state import State
from .utils import console_log


def reload() -> None:
    """
    This function is used to reload the current screen.
    """
    manager = App.get_running_app().root
    try:
        manager.current = ''
    except ScreenManagerException:
        pass


class History(EventDispatcher):
    """
    This class exposes useful methods and properties that let you navigate
    back and forth through the screen manager, and manipulate the contents
    of the history stack.
    """
    loading = False
    stack = ListProperty()
    popstate = ObjectProperty()
    index = BoundedNumericProperty(0, min=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda n: self.stack.append(
            State(App.get_running_app().root.current)
        ))

    @property
    def lenght(self) -> int:
        """
        Returns an Integer representing the number of elements in the history,
        including the currently loaded screen.
        """
        return len(self.stack)

    @property
    def state(self) -> State:
        """
        Returns an any value representing the state at the top of the history
        stack.
        """
        return self.stack[self.index]

    def back(self) -> None:
        """
        This method goes to the previous screen in session history, equivalent
        to history.go(-1).

        Calling this method to go back beyond the first screen in the session
        history has no effect and doesn't raise an exception.
        """
        self.go(-1)

    def forward(self) -> None:
        """
        This method goes to the next screen in session history, the equivalent
        to history.go(1).

        Calling this method to go forward beyond the most recent screen in the
        session history has no effect and doesn't raise an exception.
        """
        self.go(1)

    def go(self, delta: int = 0) -> None:
        """
        The position in the history to which you want to move, relative to the
        current screen. A negative value moves backwards, a positive value moves
        forwards. So, for example, history.go(2) moves forward two screens and
        history.go(-2) moves back two screens. If no value is passed or if delta
        equals 0, it has the same result as calling reload().

        If you specify an out-of-bounds value (for instance, specifying -1 when
        there are no previous screen in the session history), this method silently
        has no effect.
        """
        self.loading = True
        manager = App.get_running_app().root

        if not delta:
            reload()
        else:
            try:
                self.index += delta
                manager.current = str(self.state)
            except ValueError:
                pass
        self.loading = False

    def push_state(self, name: str, **kwargs) -> None:
        """
        Pushes the given data onto the session history stack with the specified
        data.
        """
        self.stack.append(State(name, **kwargs))

    def replace_state(self, **kwargs) -> None:
        """
        Updates the most recent entry on the history stack to have the specified
        data.
        """
        self.state.update(**kwargs)

    def on_state(self, instance, value):
        """
        This method must be binded to the 'current' property of the screen manager
        so that it can register the screen changes. For example:

        >> manager.bind(current=history.on_state)
        """
        if not self.loading:
            for s in self.stack[self.index + 1:-1]:
                self.popstate = s
            self.stack = self.stack[0:self.index + 1]
            self.stack.insert(self.index + 1, State(value))
            self.index += 1

    def on_index(self, instance, value):
        """
        Log the current state of the stack.
        """
        if int(os.environ.get("HISTORY_LOG", "0")):
            console_log(self.stack, value)

    def on_stack(self, instance, value):
        """
        Change the maximum value allowed for the index property.
        """
        prop = getattr(self, 'property')
        prop('index').set_max(self, self.lenght - 1)

    def on_popstate(self, instance, value):
        pass
