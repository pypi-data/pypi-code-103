"""Module containing base action classes used as the foundation of the package. """
import copy
import inspect
import logging
import warnings
from typing import List, Callable, Union, MutableSequence, Optional

from ..mixin import InstanceRegistry, ClassProperty


logger = logging.getLogger(__name__)


class Action(InstanceRegistry):
    UUID_PREFIX = 'action-'

    def __init__(self,
                 action: Callable,
                 *default_args,
                 parent_identifier: str = None,
                 **default_kwargs,
                 ):
        """
        Base class for storing and tracking actions (functions) to be executed. Effectively this is a wrapper class
        which provides easy access to attributes relevant to automation (name, signature, kwarg defaults, etc.).

        :param action: action (function) to execute when called
        :param default_args: default arguments for the action. Effectively turns arguments into keyword arguments.
        :param default_kwargs: default kwargs for the action. Overrides kwarg defaults of the provided action.
        :param parent_identifier: identifier string of a parent of the action (used for action-instance associations
            where an action is specific to a parent instance)
        """
        # todo consider implementing action removal
        if self.action_is_registered(action, parent_identifier=parent_identifier) is True:
            raise ValueError(
                f'The action "{action}" is already registered, use {self.__class__.__name__}.register_action instead'
            )
        if callable(action) is False:
            raise TypeError(f'the provided action {action} is not callable')
        InstanceRegistry.__init__(self)
        self.action = action
        self.__doc__ = inspect.getdoc(action)
        self.signature = inspect.signature(action)
        self.default_args = default_args
        self.logger = logger.getChild(f'{self.__class__.__name__}.{self.name}')
        self.parent_identifier: Optional[str] = parent_identifier
        fn_kwargs = {
            name: param.default
            for name, param in self.signature.parameters.items() if param.default is not inspect._empty
        }
        fn_kwargs.update(default_kwargs)
        self.default_kwargs = fn_kwargs

    def __repr__(self):
        return f'{self.__class__.__name__}({self.action.__name__})'

    def __call__(self, *args, **kwargs):
        self.logger.debug(f'calling {self.name} with args {args} and kwargs {kwargs}')
        return self.action(*args, **kwargs)

    def compare_equality(self, other: Union[str, 'Action', Callable], parent_identifier: str = None) -> bool:
        """
        Performs a comparison between the other and this instance. Matches instances, action names, and callable names.

        :param other: other instance to compare
        :param parent_identifier: parent identifier (parent instance association; if this is defined, the other instance
            must match both name and parent identifier)
        :return: whether other matches self
        """
        if other is self:
            return True
        if isinstance(other, Action):
            parent_identifier = other.parent_identifier
            name_match = self.name == other.name
        elif type(other) is str:
            name_match = self.name == other

        elif callable(other):
            name_match = self.action == other
        else:
            raise TypeError(f'the provided type {type(other)} is not comparable')
        if name_match and parent_identifier is not None:
            if self.parent_identifier == parent_identifier:
                return True
            return False
        return name_match

    def __eq__(self, other: Union[str, 'Action']) -> bool:
        """compares the other to various attributes of self"""
        return self.compare_equality(other)

    @property
    def name(self) -> str:
        """action (function) name"""
        return self.action.__name__

    @property
    def return_type(self):
        """the return type of the action"""
        if self.signature.return_annotation is inspect._empty:
            return None
        return self.signature.return_annotation

    @classmethod
    def action_is_registered(cls,
                             action: Union[str, Callable, "Action"],
                             parent_identifier: str = None,
                             ) -> bool:
        """
        Checks whether the provided action is registered as a Action instance.

        :param action: action to check
        :param parent_identifier: parent identifier (parent instance association; if this is defined, the other instance
            must match both name and parent identifier)
        :return: whether action is registered
        """
        for instance in cls.class_registry:
            if instance.compare_equality(action, parent_identifier=parent_identifier):
                return True
        return False

    @classmethod
    def register_action(cls,
                        action: Union[str, Callable, "Action"],
                        parent_identifier: str = None,
                        ) -> "Action":
        """
        Registers a new instance or returns an existing instance if the action is already registered.

        :param action: action method
        :param parent_identifier: identifier string of a parent of the action (used for action-instance associations
            where an action is specific to a parent instance)
        :return: Action instance
        """
        # catch class instance
        if isinstance(action, Action):
            return action
        elif hasattr(action, 'action') and isinstance(action.action, Action):
            return action.action
        # match action to instance
        for instance in cls.class_registry:
            if instance.compare_equality(action, parent_identifier=parent_identifier):
                return instance
        # otherwise return a new instance
        return cls(
            action,
            parent_identifier=parent_identifier,
        )

    @classmethod
    def register_actions(cls, *actions: Union[str, Callable, "Action"]) -> List["Action"]:
        """
        Registers multiple actions at once

        :param actions: action methods to be registered
        :return: list of actions which were registered
        """
        return [
            cls.register_action(action) for action in actions
        ]

    @classmethod
    def get_registered_actions(cls) -> List["Action"]:
        """returns a list of registered Action instances"""
        warnings.warn(
            'get_registered_actions has been deprecated, retrieve registered_actions directly',
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.registered_actions

    @ClassProperty
    def registered_actions(cls) -> List["Action"]:
        """a list of registered Action instances"""
        return cls.class_registry

    @classmethod
    def get_registered_action_names(cls) -> List[str]:
        """returns a list of the names of the registered Scheduler Actions"""
        warnings.warn(
            'get_registered_action_names has been deprecated, retrieve registered_action_names directly',
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.registered_action_names

    @ClassProperty
    def registered_action_names(cls) -> List[str]:
        """a list of the names of the registered Actions"""
        return [action.name for action in cls.registered_actions]

    @property
    def returns_bool(self) -> bool:
        """whether the action return type bool"""
        return self.return_type is bool


class EvalAction(Action):
    def __init__(self,
                 action: Callable,
                 *default_args,
                 **default_kwargs,
                 ):
        """
        Subclass of an Action where the action must return a bool. Note that this class does not enforce this, but
        warns the user if a non-bool type hint was detected.

        :param action: action method to execute when called
        :param default_args: default arguments for the action
        :param default_kwargs: default kwargs for the action
        """
        super().__init__(
            action=action,
            *default_args,
            **default_kwargs,
         )
        if self.return_type is not bool:
            warnings.warn(f'The action "{self.name}" provided as an EvalAction does not have a bool return type')


class ActionList(MutableSequence):
    def __init__(self, *actions: Action):
        """
        A manager for a list of Actions.

        :param actions: actions to sequence
        """
        self._action_list: List[Action] = []
        for action in actions:
            self.append(action)

    def __repr__(self):
        return f'{self.__class__.__name__}[{", ".join([str(action) for action in self._action_list])}]'

    @staticmethod
    def _ensure_type(action: Union[str, Action]) -> Action:
        """Ensures that the provided action is of the correct type for the list"""
        return Action.register_action(action)

    def __getitem__(self, item) -> Action:
        return self._action_list[item]

    def __setitem__(self, key, value: Action):
        value = self._ensure_type(value)
        self._action_list[key] = value

    def __delitem__(self, key):
        del self._action_list[key]

    def __len__(self):
        return len(self._action_list)

    def __copy__(self):
        # provides a copy of the class while preventing mutation of the actions in the instance itself
        return self.__class__(
            *[copy.copy(action) for action in self]
        )

    def insert(self, index: int, action: Action) -> None:
        """
        Inserts the provided action into the Action list

        :param index: index to insert at
        :param action: action object to insert
        :return:
        """
        action = self._ensure_type(action)
        self._action_list.insert(
            index,
            action,
        )
