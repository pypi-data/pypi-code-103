import logging
from collections import defaultdict
from typing import Union, Optional, Callable, DefaultDict, List, Dict, TypeVar, Type, Generic

import zmq
from pydantic import ValidationError, BaseModel

from openmodule.config import settings
from openmodule.models.base import ZMQMessage
from openmodule.utils.schema import Schema


class Listener:
    def __init__(self, message_class: Type[ZMQMessage], filter: Optional[Dict], handler: Callable):
        self.filter = filter
        self.handler = handler
        self.message_class = message_class

    def matches(self, message: Dict):
        if self.filter is None:
            return True
        else:
            return message.items() >= self.filter.items()


EventArgs = TypeVar("EventArgs")


class EventListener(Generic[EventArgs], list):
    log: Optional[logging.Logger]

    def __init__(self, *args, log=None, raise_exceptions=False):
        super().__init__(args)
        self.raise_exceptions = raise_exceptions
        self.log = log or logging

    def __call__(self, *args: EventArgs):
        for f in self:
            try:
                f(*args)
            except zmq.ContextTerminated:
                raise
            except Exception as e:
                if self.raise_exceptions:
                    raise
                else:
                    self.log.exception(e)


ZMQMessageSub = TypeVar('ZMQMessageSub', bound=ZMQMessage)


class MessageDispatcher:
    def __init__(self, name=None, *, raise_validation_errors=False, raise_handler_errors=False):
        """
        :param name: optionally name the dispatcher for logging purposes
        :param raise_validation_errors: if true and received messages do not match a validation error is raised,
                                        this is useful in restricive code or testcases
        :param raise_handler_errors: if true and a message handler raises an exception, the exception is raised,
                                     this is useful in restricive code or testcases
        """
        self.name = name
        self.log = logging.getLogger(f"{self.__class__.__name__}({self.name})")
        self.listeners: DefaultDict[bytes, List[Listener]] = defaultdict(list)
        self.raise_validation_errors = raise_validation_errors
        self.raise_handler_errors = raise_handler_errors

    def unregister_handler(self, listener: Listener):
        for topic, listeners in self.listeners.items():
            try:
                listeners.remove(listener)
            except ValueError:
                pass

    def _is_test_handler(self, handler):
        """
        this breaks separation a bit by including test specific code in the main module
        but it improves developer usability drastically
        """
        if settings.TESTING and "Mock" in str(handler):
            return True
        else:
            return False

    def register_handler(self, topic: Union[bytes, str],
                         message_class: Type[ZMQMessageSub],
                         handler: Callable[[ZMQMessageSub], None], *,
                         filter: Optional[Dict] = None,
                         match_type=False,
                         register_schema=True):
        """
        registers a message handler. without any filters all messages from the topic are
        sent to the message handler.
        :param filter: a dictionary of values which must match in order for the message to
                       be further processed
        :param match_type: if set to true the message_class's type field is used as a filter.
                           equivalent to setting filter={"type": message_class.fields["type"].default}
        """

        if hasattr(topic, "encode"):
            topic = topic.encode()

        if match_type:
            assert "type" in message_class.__fields__ and message_class.__fields__["type"].default, (
                "Your message class definition does not set a `type` field, or the type field "
                "does not have a default value!"
            )
            filter = filter or {}
            filter["type"] = message_class.__fields__["type"].default

        listener = Listener(message_class, filter, handler)
        self.listeners[topic].append(listener)

        if register_schema and not self._is_test_handler(handler):
            Schema.save_message(topic, message_class, handler, filter)

        return listener

    def dispatch(self, topic: bytes, message: Union[Dict, BaseModel]):
        if isinstance(message, BaseModel):
            message = message.dict()

        listeners = self.listeners.get(topic, [])
        for listener in listeners:
            if listener.matches(message):
                self.execute(listener, message)

    def execute(self, listener: Listener, message: Dict):
        try:
            parsed_message = listener.message_class(**message)
        except ValidationError as e:
            if self.raise_validation_errors:
                raise e from None
            else:
                self.log.exception("Invalid message received")
        else:
            try:
                listener.handler(parsed_message)
            except zmq.ContextTerminated:
                raise
            except Exception as e:
                if self.raise_handler_errors:
                    raise e from None
                else:
                    self.log.exception("Error in message handler")


class SubscribingMessageDispatcher(MessageDispatcher):
    def __init__(self, subscribe: Callable[[bytes], None], name=None, *, raise_validation_errors=False,
                 raise_handler_errors=False, unsubscribe: Optional[Callable[[bytes], None]] = None):
        super().__init__(name=name, raise_validation_errors=raise_validation_errors,
                         raise_handler_errors=raise_handler_errors)
        self.subscribe = subscribe
        self.unsubscribe = unsubscribe

    def register_handler(self, topic: Union[bytes, str],
                         message_class: Type[ZMQMessageSub],
                         handler: Callable[[ZMQMessageSub], None], *,
                         filter: Optional[Dict] = None,
                         register_schema=True,
                         match_type=False):
        if topic and hasattr(topic, "encode"):
            topic = topic.encode()
        self.subscribe(topic)
        return super().register_handler(topic, message_class, handler, filter=filter,
                                        register_schema=register_schema, match_type=match_type)

    def unregister_handler(self, listener: Listener):
        super().unregister_handler(listener)

        warn_no_unsubscribe = False
        for topic, listeners in self.listeners.items():
            if not listeners:
                if self.unsubscribe:
                    self.unsubscribe(topic)
                else:
                    warn_no_unsubscribe = True
                    break

        if warn_no_unsubscribe:
            self.log.warning("All handlers were unregistered from a topic, but no unsubscribe method was configured. "
                             "This may cause a performance overhead if too many unused subscriptions are kept. "
                             "Consider passing a unsubscribe method.")


class ZMQMessageDispatcher(SubscribingMessageDispatcher):
    def __init__(self, sub_socket: zmq.Socket, name=None, *, raise_validation_errors=False, raise_handler_errors=False):
        super().__init__(
            subscribe=lambda x: sub_socket.subscribe(x),
            unsubscribe=lambda x: sub_socket.unsubscribe(x),
            name=name,
            raise_validation_errors=raise_validation_errors,
            raise_handler_errors=raise_handler_errors
        )
