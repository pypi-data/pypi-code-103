# coding: utf-8
"""
The :mod:`piaf.agent` module contains everything you need to create your own agents.

According to FIPA specification:

.. epigraph::

    "An agent is a computational process that implements the autonomous, communicating
    functionality of an application. Agents communicate using an Agent Communication
    Language. An Agent is the fundamental actor on an [Agent Platform] which combines
    one or more service capabilities, as published in a service description, into a
    unified and integrated execution model. An agent must have at least one owner, for
    example, based on organisational affiliation or human user ownership, and an agent
    must support at least one notion of identity. This notion of identity is the Agent
    Identifier (AID) that labels an agent so that it  may be distinguished unambiguously
    within the Agent Universe. An agent may be registered at a number of transport
    addresses at which it can be contacted."

    -- `FIPA000023 <http://www.fipa.org/specs/fipa00023/SC00023K.html#_Toc75950978>`_

Currently, the Agent API supports:

* Communication with other Agents
* Agent IDentifier
* Multi transport addresses

It doesn't support:

* Agent ownership

"""
import copy
import datetime
import enum
import logging
import asyncio

import piaf.comm
import piaf.comm.mts
import piaf.exceptions as ex

from typing import Sequence, Union, Iterable, MutableSequence, TYPE_CHECKING

if TYPE_CHECKING:
    import piaf.behavior
    import piaf.platform

__all__ = ["Agent", "AgentState"]


class AgentState(enum.Enum):
    """
    Represents an agent state.

    According to FIPA specification (http://www.fipa.org/specs/fipa00023/), an agent
    can have 6 states:

    **INITIATED**
        Agent has been created or installed on the Agent Platform but is not invoked
        yet.
    **ACTIVE**
        Agent has been invoked and is now running.
    **SUSPENDED**
        Agent is suspended.
    **WAITING**
        Agent is waiting something.
    **TRANSIT**
        Agent is transiting between different platforms. Not supported for now.
    **UNKNOWN**
        Agent has been deleted or doesn't exist yet.

    More information in the specification.
    """

    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name

    INITIATED = enum.auto()
    ACTIVE = enum.auto()
    SUSPENDED = enum.auto()
    WAITING = enum.auto()
    TRANSIT = enum.auto()
    UNKNOWN = enum.auto()


class Agent:
    """
    :class:`Agent` is the base class for all user agents.

    When creating an agent, you must provide this agent's identity and the platform
    facade that it will use to access vital functionalities like querying / updating
    the agent's state or communicating with other agents.

    You can use this class directly although your agent will be useless. We recommend
    subclassing.

    When subclassing the :class:`Agent` class, you can safely:

    * Extend the constructor to add new instructions
    * Extend all methods except the :meth: `run` method
    * Add custom methods

    Here is an example:

    .. code-block:: python

        from piaf.agent import Agent
        from piaf.platform import AgentPlatform
        from piaf.comm.mts import MemoryMessageTransferHandler

        class MyAgent(Agent):
            def __init__(aid, platform, foo, *args, **kwargs):
                '''Extra argument and attribute in the constructor.'''
                super().__init__(aid, platform, *args, **kwargs)
                self.foo = foo

            def add_behavior(self, behavior):
                '''Extend method to add some logs.'''
                super().add_behavior(behavior)
                self.agent.logger.info(
                    "Added a behavior to agent %s", self.aid.short_name
                )

            def bar(self):
                '''Custom method.'''
                pass

        if __name__ == "__main__":
            ap = AgentPlatform()

            async def main():
                # Setup platform
                await ap.start()

                # Add agent
                aid = await ap.agent_manager.create("test", foo="foo")
                await ap.agent_manager.invoke(aid)

            loop = asyncio.get_event_loop()
            loop.set_debug(True)
            try:
                loop.create_task(main())
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            finally:
                loop.run_until_complete(ap.stop())
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

    """

    #: How much time (in seconds) the agent will sleep before checking if it is still
    #: in WAITING/SUSPENDED state.
    CLEANUP_DELAY = 1

    def __init__(
        self,
        aid: "piaf.comm.AID",
        platform: "Union[piaf.platform.AgentPlatformFacade, piaf.platform.AgentPlatform]",
        *args,
        **kwargs
    ):
        """
        Create a new Agent with the provided information.

        :param aid: this agent's identifier
        :param platform: the platform (or a facade) where this agent is deployed
        """
        self.logger = logging.getLogger(type(self).__name__)
        self._aid = copy.deepcopy(aid)
        self._behaviors: MutableSequence[asyncio.Future[None]] = []
        self._platform = platform
        self._mailbox = piaf.comm.mts.MailBox()

    @property
    def state(self) -> "AgentState":
        """
        Get this agent state.

        Readonly property that query the platform to get this agent's state.
        """
        return self._platform.get_state(self._aid)

    @property
    def state_sync(self):
        """Synchronization primitive."""
        return self._platform.get_state_condition(self._aid)

    @property
    def aid(self) -> "piaf.comm.AID":
        """
        Get the agent's identifier.

        Please note that the retrieved object is a copy and can be safely modified
        without affecting the agent.
        Readonly property.
        """
        return copy.deepcopy(self._aid)

    @property
    def mailbox(self) -> "piaf.comm.mts.MailBoxDelegate":
        """
        Get a reference to the internal's agent mailbox.

        You will get limited writing access.
        """
        return piaf.comm.mts.MailBoxDelegate(self._mailbox)

    async def wait(self) -> None:
        """Put this agent in WAITING state."""
        await self._platform.wait(self._aid)

    async def suspend(self) -> None:
        """Suspend this agent."""
        await self._platform.suspend(self._aid)

    async def quit(self) -> None:
        """Shutdown the agent as soon as possible."""
        await self._platform.quit(self._aid)

    def add_behavior(
        self, behavior: "piaf.behavior.Behavior"
    ) -> "asyncio.Future[None]":
        """
        Add a behavior to this agent.

        :param behavior: the behavior (an instance) you want to add.
        """
        task = asyncio.ensure_future(behavior.run())
        self._behaviors.append(task)
        return task

    async def run(self) -> None:
        """
        Coroutine in charge of running the agent.

        .. warning:: You should not override or extend this method or you agent might
                     not run correctly.
        """
        try:
            while self._running() and self._behaviors:
                # Wait until state is active or agent quits
                # If agent quits while being paused or suspended, we must unlock the agent
                async with self.state_sync:
                    await self.state_sync.wait_for(
                        lambda: self.state == AgentState.ACTIVE
                        or self.state == AgentState.UNKNOWN
                    )

                # If agent is active
                if self.state == AgentState.ACTIVE:
                    # Get done and pending tasks
                    done, pending = await asyncio.wait(
                        self._behaviors, timeout=self.CLEANUP_DELAY
                    )

                    # Display done behaviors with exception
                    self._display_bhv_failures(done)

                    # Update running behaviors list
                    self._behaviors = list(pending)

            # Inform the platform that we are quitting
            await self._platform.quit(self._aid)

        except asyncio.CancelledError:
            # Ignore error
            pass

        finally:
            # Cancel running behaviors
            if self._behaviors:
                for bhv in self._behaviors:
                    bhv.cancel()

                await asyncio.gather(*self._behaviors, return_exceptions=True)

            # Display behavior failures
            self._display_bhv_failures(self._behaviors)

            self.logger.info(
                "[%s]: If this is dying, I don't think much of it.",
                self._aid.short_name,
            )

    async def receive(
        self, template: "piaf.comm.MessageTemplate" = piaf.comm.MT_ALL()
    ) -> "piaf.comm.Message":
        """
        Query this agent's mailbox to retrieve a message matching the provided template.

        Templates are applied to ACL Messages, not Envelopes.
        Note that this is a blocking receive, meaning that the coroutine ends when a
        message is found. The default template match any kind of messages.

        :param template: the message template used to search messages
        """
        return await self._mailbox.get(template)

    async def receive_nowait(
        self, template: "piaf.comm.MessageTemplate" = piaf.comm.MT_ALL()
    ) -> Union[None, "piaf.comm.Message"]:
        """
        Query this agent's mailbox to retrieve a message matching the provided template.

        Templates are applied to ACL Messages, not Envelopes.
        Contrary to :meth:`receive`, this method will return ``None`` if no matching
        message is found. The default template matches all messages.

        :param template: the message template used to search messages
        """
        return await self._mailbox.get_nowait(template)

    def send(self, message: "piaf.comm.ACLMessage") -> None:
        """
        Send a message.

        The underlying implementation will use information provided in the message to
        contact receivers.

        :param message: the message to send
        """
        if message.receiver is None:
            raise ex.IllegalArgumentException("Message must have a receiver")

        if not isinstance(message.receiver, Sequence):
            to = (message.receiver,)
        else:
            to = message.receiver  # type: ignore

        message.sender = self.aid

        envelope = (
            piaf.comm.Envelope.Builder()
            .from_(self.aid)
            .to(to)
            .acl_representation("piaf.acl.repr.obj")
            .date(datetime.datetime.now())
            .build()
        )

        self._platform.send(piaf.comm.Message(envelope, message))

    def _running(self) -> bool:
        return (
            self.state == AgentState.ACTIVE
            or self.state == AgentState.SUSPENDED
            or self.state == AgentState.WAITING
        )

    def _display_bhv_failures(self, tasks: Iterable["asyncio.Future[None]"]):
        for task in filter(
            lambda e: not e.cancelled() and e.exception() is not None, tasks
        ):
            self.logger.exception(
                "%s: Behavior failure :",
                self.aid.short_name,
                exc_info=task.exception(),
            )
