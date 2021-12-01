# coding: utf-8
import enum
import asyncio
import logging
import importlib
import contextlib
import copy

import piaf.comm.mts
import piaf.comm
import piaf.exceptions as ex

from typing import (
    Type,
    Optional,
    MutableMapping,
    MutableSequence,
    Sequence,
    Any,
    TYPE_CHECKING,
)

from piaf.service import AMSService

if TYPE_CHECKING:
    import piaf.agent  # noqa

__all__ = ["AgentPlatformFacade", "AgentManager", "PlatformState", "AgentPlatform"]


class AgentPlatformFacade:
    """
    Facade limiting access to platform functionalities.

    This facade is provided to show the interface between user agents and the platform
    but should be used directly.
    """

    def __init__(self, platform: "AgentPlatform", is_service: bool = False):
        """
        Create a new :class:`AgentPlatformFacade` backed by the provided platform.

        :param platform: the real platform behind this facade
        """
        self._platform = platform
        self._is_service = is_service

    async def suspend(self, agent: "piaf.comm.AID") -> None:
        """
        Suspend an agent.

        Even if it is possible to suspend an other agent by providing its AID, it
        should not be done. Only suspend yourself !

        :param agent: the AID of the agent
        """
        await self._platform.agent_manager.suspend(agent)

    async def wait(self, agent: "piaf.comm.AID") -> None:
        """
        Put an agent in WAITING state.

        Even if it is possible to put in waiting state an other agent by providing
        its AID, it should not be done.

        :param agent: the AID of the agent
        """
        await self._platform.agent_manager.wait(agent)

    async def quit(self, agent: "piaf.comm.AID") -> None:
        """
        Make this agent quit.

        It will request the agent to die, but it provide the ability to shutdown
        properly. Again, use it with your agent's AID, not others.

        :param agent: the AID of the agent
        """
        await self._platform.agent_manager.quit(agent)

    def send(self, message: "piaf.comm.Message") -> None:
        """
        Send the provided message.

        This method can raise several exceptions if there is any issue when sending the
        message.

        :param message: the message to send.
        """
        self._platform._acc.forward(message)

    def get_state(self, agent: "piaf.comm.AID") -> "piaf.agent.AgentState":
        """
        Get the state of the agent.

        Only use your agent's AID.

        :param agent: the agent's AID
        """
        return self._platform.agent_manager.get_state(agent)

    def get_state_condition(self, agent: "piaf.comm.AID") -> asyncio.Condition:
        """
        Get a condition synchronization primitive based on the agent's sate.

        Some building blocks, like user agent or behaviors need to be notified when the
        state of the agent changed. This will get a shared condition on it. Only use
        with your agent's AID.

        :param agent: the agent's AID
        """
        return self._platform.agent_manager.get_state_condition(agent)

    @property
    def name(self) -> str:
        """Get this platform's name."""
        return self._platform.name

    def __getattr__(self, name: str) -> Any:
        """
        If the agent is a service (ie requires full access to the platform), forward the call to the real platform.

        Otherwise raise an :class:`AttributeError` exception.
        """
        if self._is_service:
            return getattr(self._platform, name)
        raise AttributeError(name)


class _AgentContext:
    """
    Dataclass used to store an agent's context.

    Stored information is:

    * the agent itself
    * the agent's state
    * the task associated to the agent
    * the agent's state condition synchronization primitive

    """

    def __init__(self, agent: "piaf.agent.Agent"):
        self.agent = agent
        self.state = piaf.agent.AgentState.INITIATED
        self.task: Optional[asyncio.Future[None]] = None
        self.state_condition = asyncio.Condition()


class AgentManager:
    """
    Object responsible of managing agents on a platform.

    This manager is dedicated to agent management and is a part of the platform.
    It is responsible of the agent's creation and death and it handle state
    modifications.

    User agents shouldn't interact with it directly but rather through the
    :class:`AgentPlatformFacade`.
    """

    def __init__(
        self, platform: "AgentPlatform", acc: "piaf.comm.mts.AgentCommunicationChannel"
    ):
        """
        Create a new manager associated to the provided platform.

        :param platform: the platform that will use this manager.
        :param acc: full access to the Agent Communication Channel
        """
        self._contexts: MutableMapping["piaf.comm.AID", "_AgentContext"] = {}
        self._platform = platform
        self._acc = acc
        self.logger = logging.getLogger(type(self).__name__)

    async def wait(self, agent: "piaf.comm.AID") -> None:
        """
        Switch the agent's state to WAITING.

        :param agent: the agent's AID
        :raise ex.StateTransitionException: if the agent's state wasn't ACTIVE
        """
        await self._switch_state(
            agent, piaf.agent.AgentState.ACTIVE, piaf.agent.AgentState.WAITING
        )

    async def suspend(self, agent: "piaf.comm.AID") -> None:
        """
        Switch the agent's state to SUSPENDED.

        :param agent: the agent's AID
        :raise ex.StateTransitionException: if the agent's state wasn't ACTIVE
        """
        await self._switch_state(
            agent, piaf.agent.AgentState.ACTIVE, piaf.agent.AgentState.SUSPENDED
        )

    async def resume(self, agent: "piaf.comm.AID") -> None:
        """
        Switch the agent's state to ACTIVE.

        :param agent: the agent's AID
        :raise ex.StateTransitionException: if the agent's state wasn't SUSPENDED
        """
        await self._switch_state(
            agent, piaf.agent.AgentState.SUSPENDED, piaf.agent.AgentState.ACTIVE
        )

    async def wake_up(self, agent: "piaf.comm.AID") -> None:
        """
        Switch the agent's state to ACTIVE.

        :param agent: the agent's AID
        :raise ex.StateTransitionException: if the agent's state wasn't WAITING
        """
        await self._switch_state(
            agent, piaf.agent.AgentState.WAITING, piaf.agent.AgentState.ACTIVE
        )

    async def create(
        self,
        agent_class: Type["piaf.agent.Agent"],
        short_name: str,
        is_service: bool = False,
        *args,
        **kwargs,
    ) -> "piaf.comm.AID":
        """
        Create a new agent.

        It will use the provided agent class and arguments to create a new agent.
        Agent's state will be set to INITIALIZED and the AID will be built according to
        the provided name and the platform parameters (name, supported schemes,
        AMS AID ...).

        :param agent_class: the agent class that is used to instantiate the agent
        :param short_name: the agent's name, without the platform name
        :param is_service: if set to True, will have full access to the platform. Use it with caution ! Default is
                           False.
        :param args: extra arguments used to instantiate the agent (other than the
                     platform)
        :param kwargs: same as ``args`` but for keywords arguments
        :raise DuplicatedNameException: if an agent with that name already exists
        :raise InvalidStateException: if the platform is not ready.
        """
        # assert self._platform.ams is not None
        if not self._platform.state == PlatformState.RUNNING:
            raise ex.InvalidStateException(self._platform.state, "add_agent")

        # Create a temporary AID
        aid = piaf.comm.AID(f"{short_name}@{self._platform.name}")
        if aid in self._contexts:
            raise ex.DuplicatedNameException(short_name)

        aid.addresses = self._acc.addresses

        # Create agent
        agent = agent_class(
            aid, AgentPlatformFacade(self._platform, is_service), *args, **kwargs
        )
        self._contexts[aid] = _AgentContext(agent)

        # Register agent to the ACC
        self._acc.register_agent_or_service(short_name, agent.mailbox)  # type: ignore

        return aid

    async def stop_all(self, timeout: float = 5.0) -> None:
        """
        Stop all running agents.

        It will first try to do a nice stop for each agent and then, if some are taking
        to much time, it will terminate the remaining.

        :param timeout: how much time is given to shutdown properly all agents (default
                        is 5s)
        """
        if not self._contexts:
            return

        tasks = [
            context.task
            for context in self._contexts.values()
            if context.task is not None
        ]

        for context in self._contexts:
            await self.quit(context)

        _, s_pending = await asyncio.wait(tasks, timeout=timeout)
        pending = list(s_pending)

        for task in pending:
            self.logger.warning(
                "[AgentManager] Agent %s did not terminate in time, "
                "emergency stop requested.",
                task.name,  # type: ignore
            )
            task.cancel()

        # No need to await termination, display exceptions and cleanup contexts
        # It is done in _clean_up task.

    async def invoke(self, agent: "piaf.comm.AID") -> None:
        """
        Invoke a previously created agent.

        The agent's state will switch from INITIATED to ACTIVE and the run method will
        be scheduled.

        :param agent: the agent that will be invoked
        """
        await self._switch_state(
            agent, piaf.agent.AgentState.INITIATED, piaf.agent.AgentState.ACTIVE
        )
        self._contexts[agent].task = asyncio.ensure_future(
            self._contexts[agent].agent.run()
        )
        self._contexts[agent].task.name = agent.short_name  # type: ignore
        self.logger.info(f"Please welcome Agent {agent.short_name} !")

        # Schedule the cleanup task
        asyncio.ensure_future(self._clean_up(agent))

    async def quit(self, agent: "piaf.comm.AID") -> None:
        """
        Instruct the agent that it should die.

        This will initiate a "gracefull" stop. The agent state will switch to UNKNOWN
        (as requested by fipa). This doesn't await the agent termination, as this method
        can be called from the agent itself.
        """
        if agent not in self._contexts:
            raise ex.IllegalArgumentException(f"Unknown agent: {agent}")

        self._contexts[agent].state = piaf.agent.AgentState.UNKNOWN
        async with self._contexts[agent].state_condition:
            self._contexts[agent].state_condition.notify_all()

    async def _clean_up(self, agent: "piaf.comm.AID") -> None:
        """
        Given an agent, wait its termination and removed it from the manager.

        :param agent: the agent to remove
        """
        task = self._contexts[agent].task
        assert task is not None
        result = (await asyncio.gather(task, return_exceptions=True))[0]

        if result is not None:
            self.logger.exception(
                "[AgentManager] Agent %s raised an exception.",
                task.name,  # type: ignore
                exc_info=result,
            )

        del self._contexts[agent]
        self._acc.forget_agent_or_service(agent.short_name)

    async def terminate(self, agent: "piaf.comm.AID") -> None:
        """
        Terminate an agent (forced).

        This will cancel the agent task and then clean up the manager. Unlike
        :meth:`stop`, this method waits the agent's death. Try to use this method only
        when the :meth:`stop` method is not working.

        :param agent: the agent to terminate
        """
        task = self._contexts[agent].task
        if task is not None:
            task.cancel()

    def get_state(self, agent: "piaf.comm.AID") -> "piaf.agent.AgentState":
        """
        Get the state of the provided agent.

        If the agent doesn't exist or is dying/dead, this method return UNKNOWN.

        :param agent: the agent
        """
        result = piaf.agent.AgentState.UNKNOWN
        with contextlib.suppress(KeyError):
            result = self._contexts[agent].state
        return result

    def get_state_condition(self, agent: "piaf.comm.AID") -> asyncio.Condition:
        """
        Get the state synchronization primitive associated to the agent.

        :param agent: the agent you want the synchronization primitive
        """
        return self._contexts[agent].state_condition

    async def _switch_state(
        self,
        agent: "piaf.comm.AID",
        from_: "piaf.agent.AgentState",
        to: "piaf.agent.AgentState",
    ) -> None:
        """
        Transition an agent's state to another.

        It cares about the current agent's state and will raise an exception if it is
        not the one expected.

        :param agent: the agent
        :param from_: what should be the current agent's state
        :param to_: the agent state you want
        :raise ex.StateTransitionException: the expected agent's state is not the
                                            current agent's state
        :raise ex.IllegalArgumentException: the agent doesn't exist (or is dead)
        """
        if agent not in self._contexts:
            raise ex.IllegalArgumentException(f"Unknown agent: {agent}")

        if not self._contexts[agent].state == from_:
            raise ex.StateTransitionException(self._contexts[agent].state, to)

        self._contexts[agent].state = to
        async with self._contexts[agent].state_condition:
            self._contexts[agent].state_condition.notify_all()
        self.logger.debug(
            "Agent %s switched its state from %s to %s", agent.name, from_, to
        )

    def get_agents(
        self, state: "Optional[piaf.agent.AgentState]" = None
    ) -> "Sequence[piaf.comm.AID]":
        """
        Get all known agents.

        If `state` is provided, the result will only contain agents having the given state.

        :param state: If provided, filter result and keep only agents having the given state.
        """
        agents = self._contexts.keys()
        if state is not None:
            agents = (agt for agt in agents if self.get_state(agt) == state)
        return [copy.deepcopy(agent) for agent in agents]


class PlatformState(enum.Enum):
    """An enum that represents what can be a platform's state."""

    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name

    INITIALIZED = enum.auto()
    RUNNING = enum.auto()
    STOPPED = enum.auto()


class AgentPlatform:
    """
    The :class:`AgentPlatform` is the object you need to run your agents.

    The first need to do is to instantiate a new platform. Them you must configure it.
    For now, the only required thing is to specify the supported schemes. Schemes are
    used for the communication between agents and is often a protocol's name (like http,
    ftp ...).
    There is one built-in scheme called `memory`.

    The next thing to do is to start the platform, using the :meth:`start` method. This
    is to ensure that the transport system and the AMS are up and ready for your agents.

    The last thing to do is to create and invoke your agents. Use the
    :class:`AgentManager` bounded to the platform to do it.

    Here is an example of how to create a platform and to run some agents::

        import asyncio
        import piaf.platform
        import piaf.comm
        import piaf.comm.mts
        import your.agent

        # Configure logging level and handler to see debug information
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler())

        # Create agent platform
        ap = piaf.platform.AgentPlatform("localhost")

        # We could add extension or MTP
        # ap.acc.register_mtp(...)

        async def main():
            '''Coroutine that starts the platform and add agents.'''
            # Before adding our agents, we need to start the platform. This ensure that
            # the AMS agent is created
            await ap.start()

            # Now we can add our agent(s)
            aid = await ap.agent_manager.create(your.agent.First, "F")
            await ap.agent_manager.invoke(aid)

            aid = await ap.agent_manager.create(your.agent.First, "S")
            await ap.agent_manager.invoke(aid)

        # We are using asyncio library to run our example
        # The program will run until you hit Ctrl+C
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

    class ACCDelegate:
        """
        Delegate object that provide mtp registration.

        Real object (delegate) is the :class:`piaf.comm.mts.AgentCommunicationChannel` instance.
        """

        def __init__(self, acc: piaf.comm.mts.AgentCommunicationChannel) -> None:
            """Create delegate with the provided real ACC."""
            self._delegate = acc

        async def register_mtp(
            self, mtp: "piaf.comm.mts.MessageTransportProtocol"
        ) -> None:
            """
            Register a new MTP and start it.

            Once registered, the ACC will be able to use the MTP to send messages. ACC doesn't allow duplicated MTPs
            (ie, MTP providing the same scheme). If you try to register a MTP with an already registered scheme, this
            method will raise an exception.

            :raise DuplicatedSchemeException: if you try to register an MTP handling an already-register scheme.
            """
            await self._delegate.register_mtp(mtp)

    def __init__(self, name: str):
        """
        Create a new :class:`AgentPlatform`. Initial state is ``INITIALIZED``.

        :param name: this platform's name.
        """
        self.logger = logging.getLogger(type(self).__name__)
        self._name = name
        self._acc = piaf.comm.mts.AgentCommunicationChannel(self)
        self._agt_manager = AgentManager(self, self._acc)
        self._tasks: MutableSequence[asyncio.Future[Optional[Any]]] = []
        self._state = PlatformState.INITIALIZED
        self.logger.info(f"Plateform {self.name} initialized")

    def load_extension(self, name: str, package: str = None) -> None:
        if self.state != PlatformState.INITIALIZED:
            raise ex.InvalidStateException(self.state, "load_extension")
        importlib.import_module(name, package)
        importlib.invalidate_caches()
        self.logger.info(f"Loaded extension {name}")

    @property
    def name(self) -> str:
        """Get this platform's name."""
        return self._name

    @property
    def schemes(self) -> Sequence[str]:
        """Get his platform supported schemes."""
        return self._acc.schemes

    @property
    def state(self) -> PlatformState:
        """Get this platform's state."""
        return self._state

    @property
    def agent_manager(self) -> AgentManager:
        """Get the agent manager associated to this platform."""
        return self._agt_manager

    @property
    def acc(self) -> "AgentPlatform.ACCDelegate":
        """Get limited access to the AgentCommunicationChannel of the platform."""
        return AgentPlatform.ACCDelegate(self._acc)

    async def start(self) -> None:
        """
        Start the platform.

        The platform state will transition to ``RUNNING`` and the AMS agent will be
        started.
        """
        # Set platform state
        self._state = PlatformState.RUNNING
        self.logger.info("Plateform is running")

        # Create AMS service
        ams_aid = await self._agt_manager.create(AMSService, "ams", True)
        await self._agt_manager.invoke(ams_aid)

    async def stop(self) -> None:
        """
        Stop this platform.

        It will stop all running agents (make them quit) and the platform's state will
        be ``STOPPED``.
        """
        await self._agt_manager.stop_all()
        await self._acc.stop()

        if self._tasks:
            for task in self._tasks:
                task.cancel()
            await asyncio.wait(self._tasks)

        self._state = PlatformState.STOPPED
        self.logger.info(f"Platform {self.name} has been stopped")
