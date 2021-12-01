# coding: utf-8
# /usr/bin/env python3
"""
The :mod:`piaf.service` module defines a set of services the platform may offer to running agents.

Except the :class:`AMSService` service, if you want to activate a service you have to start it like a regular agent.
The only key difference is that services have a privileged access to the platform. To enable this special access, you
must set the `is_service` parameter in :meth:`piaf.platform.AgentManager.create` method to `True`.
"""
from typing import (
    AbstractSet,
    Any,
    Dict,
    FrozenSet,
    List,
    Optional,
    Sequence,
    Set,
    TYPE_CHECKING,
    Tuple,
)
from piaf.agent import Agent, AgentState
from piaf.comm import (
    ACLMessage,
    AID,
    MT_NOT,
    MT_OR,
    MT_PERFORMATIVE,
    Performative,
)
from piaf.behavior import Behavior
from piaf.util import *
from datetime import datetime

if TYPE_CHECKING:
    import piaf.comm
    import piaf.platform


class AMSService(Agent):
    """
    Special agent providing Agent Management Services.

    The AMS is a required component of the agent platform. It allows others agents to query the platform capabilities
    and other agents AIDs.

    The AMS uses the underlying platform to discover registered agents.

    .. warning:: For now, the AMS agent only supports the search request.

    Specification: http://fipa.org/specs/fipa00023/SC00023K.html
    """

    SEARCH_FUNC = "search"

    def __init__(
        self,
        aid: "piaf.comm.AID",
        platform: "piaf.platform.AgentPlatform",
        *args,
        **kwargs,
    ):
        """
        Create a new AMS Agent with the provided information.

        :param aid: this agent's identifier
        :param platform: the platform where this AMS agent is deployed
        """
        super().__init__(aid, platform, *args, **kwargs)

        # Add behaviors
        self.add_behavior(_AMSRequestBehavior(self))
        self.add_behavior(_HandleInvalidMessageBehavior(self))


class _BaseRequestBehavior(FIPARequestProtocolBehavior, metaclass=ABCMeta):
    """Base implementation for request protocol handling by both the  AMS and the DF."""

    #: Acceptable messages for this Request protocol
    VALID_MSG_TEMPLATE = MT_OR(
        MT_PERFORMATIVE(Performative.REQUEST), MT_PERFORMATIVE(Performative.CANCEL)
    )

    def check_message(self, msg: "ACLMessage") -> bool:
        """
        Check the content of the provided message.

        * Not a sequence      -> NOT_UNDERSTOOD, unsupported-value
        * Length == 0         -> REFUSE, missing-parameter
        * First param not str -> REFUSE, unrecognized-parameter-value

        :param msg: message to check
        :return: True if message is ok, False otherwise
        """
        content = msg.content
        result = False

        if not isinstance(content, (List, Tuple, Set)):
            self.agent.send(
                not_understood_message_from_request(msg, "Unsupported value: content")
            )

        elif len(content) == 0:
            self.agent.send(
                refuse_message_from_request(msg, "Missing parameter: function_name")
            )

        elif not isinstance(content[0], str):
            self.agent.send(
                refuse_message_from_request(
                    msg, f"Unrecognized parameter value: function_name, {content[0]}"
                )
            )

        else:
            result = True

        return result

    @property
    def msg_template(self) -> "piaf.comm.MessageTemplate":
        return _BaseRequestBehavior.VALID_MSG_TEMPLATE


class _AMSRequestBehavior(_BaseRequestBehavior):
    """Custom implementation of the class:`FIPARequestProtocolBehavior` for the AMS agent."""

    async def on_valid_request(self, msg: "ACLMessage") -> None:
        """
        Depending on the message content, the AMS agent is executing the request.

        For now, only the SEARCH function is supported.

        :param msg: the request message to handle
        """
        # If function is the search function
        if msg.content[0] == AMSService.SEARCH_FUNC:
            await self._handle_search_request(msg)

        # Unsupported function
        else:
            self.agent.send(
                refuse_message_from_request(
                    msg, f"Unsupported function: {msg.content[0]}"
                )
            )

    async def _handle_search_request(self, msg: "ACLMessage"):
        """Execute the `search` function if possible and send the reply."""
        # At least the mandatory parameter df-agent-description
        if len(msg.content) < 2:
            self.agent.send(
                refuse_message_from_request(
                    msg, "Missing argument: ams-agent-description"
                )
            )
            return

        # At most 2 parameters : df-agent-description and the optional parameter search-constraints
        if len(msg.content) > 3:
            self.agent.send(
                refuse_message_from_request(msg, "Unexpected argument count")
            )
            return

        # df-agent-description must be a DFAgentDescription
        if not isinstance(msg.content[1], AMSAgentDescription):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: ams-agent-description, {msg.content[1]}",
                )
            )
            return

        # If present, search-constraints parameter must be a SearchConstraints
        if len(msg.content) == 3 and not isinstance(msg.content[2], SearchConstraints):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: search-constraints, {msg.content[2]}",
                )
            )
            return

        ams_agent_description = msg.content[1]
        am = self.agent._platform.agent_manager
        agents = am.get_agents(ams_agent_description.state)
        agt_descriptions = []

        # Perform the search
        self.agent.send(agree_message_from_request(msg))

        if ams_agent_description.name is not None:
            if ams_agent_description.name in agents:
                agt_descriptions.append(
                    AMSAgentDescription(
                        ams_agent_description.name,
                        None,
                        am.get_state(ams_agent_description.name),
                    )
                )

        else:
            agt_descriptions = [
                AMSAgentDescription(agent, None, am.get_state(agent))
                for agent in agents
            ]

        # Constrain if applicable
        if len(msg.content) == 3:
            max_results = msg.content[2].max_results
            if max_results is not None:
                agt_descriptions = agt_descriptions[:max_results]

        # Send the result
        self.agent.send(inform_message_from_request(msg, agt_descriptions))


class _HandleInvalidMessageBehavior(Behavior):
    """
    Handle all messages not matching the template defined in :class:`_BaseRequestBehavior`.

    If such message is found then this behavior sends a `NOT_UNDERSTOOD` message.
    """

    def done(self) -> bool:
        """Infinite behavior."""
        return False

    async def action(self) -> None:
        """Wait for messages and send `NOT_UNDERSTOOD` message."""
        msg = await self.agent.receive(MT_NOT(_BaseRequestBehavior.VALID_MSG_TEMPLATE))
        self.agent.send(
            not_understood_message_from_request(
                msg.acl_message, f"Unsupported Act: {msg.acl_message.performative}"
            )
        )


class AMSAgentDescription:
    """
    :class:`AMSAgentDescription` objects are returned when querying the AMS agent about agents in the platform.

    Fields are:

    - **name**: the :class:`AID` of the agent
    - **ownership**: how owns it
    - **state**: the agent current state (at the time the AMS queried it)

    It is part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(
        self,
        name: Optional[AID] = None,
        ownership: Optional[str] = None,
        state: Optional[AgentState] = None,
    ) -> None:
        self.name: Optional[AID] = name
        self.ownership: Optional[str] = ownership
        self.state: Optional[AgentState] = state

    def __eq__(self, o: object) -> bool:
        return o is self or (
            isinstance(o, type(self))
            and o.name == self.name
            and o.ownership == self.ownership
            and o.state == self.state
        )


class AgentPlatformService:
    """
    Description of a platform service.

    Fields are:

    - **name**: name of the service
    - **type**: type of the service. For example: "fipa.mtp.http"
    - **addresses**: a sequence of urls where to access the service    

    It is part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(self, name: str, type: str, addresses: Sequence[str]) -> None:
        self.name: str = name
        self.type: str = type
        self.addresses: Sequence[str] = addresses

    def __eq__(self, o: object) -> bool:
        return o is self or (
            isinstance(o, type(self))
            and o.name == self.name
            and o.type == self.type
            and o.addresses == self.addresses
        )


class AgentPlatformDescription:
    """
    Description of the AgentPlatform.

    Fields are:

    - **name**: the name of the agent platform
    - **ap_services**: a set of services this platform provides

    It is part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(self, name: str, ap_services: Set[AgentPlatformService]) -> None:
        self.name: str = name
        self.ap_services: Set[AgentPlatformService] = ap_services

    def __eq__(self, o: object) -> bool:
        return o is self or (
            isinstance(o, type(self))
            and o.name == self.name
            and o.ap_services == self.ap_services
        )


class Property:
    """
    :class:`Property` objects are usefull for specifying parameter/value pairs.

    Part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(self, name: str, value: Any) -> None:
        self.name: str = name
        self.value: Any = value

    def __eq__(self, o: object) -> bool:
        return o is self or (
            isinstance(o, type(self)) and o.name == self.name and o.value == self.value
        )


class DFService(Agent):
    """
    The DFService acts like yellow pages

    This service stores agent capabilities on demand (meaning that each agent must register itself to this service). It
    supports all operations defined in the fipa specification :

    - register: register a new agent description
    - deregister: remove an agent description
    - search: perform a search (with a search pattern and constraints) against all records
    - modify: modify an existing record

    .. note:: The DFService currently doesn't support the federated DF mechanism desfined in fipa specification.
    """

    REGISTER_FUNC = "register"
    DEREGISTER_FUNC = "deregister"
    SEARCH_FUNC = "search"
    MODIFY_FUNC = "modify"

    def __init__(
        self,
        aid: "piaf.comm.AID",
        platform: "piaf.platform.AgentPlatform",
        *args,
        **kwargs,
    ):
        super().__init__(aid, platform, *args, **kwargs)

        # Store agents and services descriptions
        self.storage: Dict[AID, DFAgentDescription] = {}

        self.add_behavior(_HandleInvalidMessageBehavior(self))
        self.add_behavior(_DFRequestBehavior(self))


class _DFRequestBehavior(_BaseRequestBehavior):
    async def on_valid_request(self, msg: "ACLMessage") -> None:
        """
        Depending on the message content, the DF agent is executing the request.

        For now, only the REGISTER function is supported.

        :param msg: the request message to handle
        """
        # If function is the register function
        if msg.content[0] == DFService.REGISTER_FUNC:
            await self._handle_registration_request(msg, True)

        # If function is the deregister function
        elif msg.content[0] == DFService.DEREGISTER_FUNC:
            await self._handle_registration_request(msg, False)

        # If function is the search function
        elif msg.content[0] == DFService.SEARCH_FUNC:
            await self._handle_search_request(msg)

        # If function is the modify function
        elif msg.content[0] == DFService.MODIFY_FUNC:
            await self._handle_modify_request(msg)

        # Unsupported function
        else:
            self.agent.send(
                refuse_message_from_request(
                    msg, f"Unsupported function: {msg.content[0]}"
                )
            )

    async def _handle_registration_request(
        self, msg: "ACLMessage", register: bool
    ) -> None:
        """
        Handle a register / deregister request.

        :param msg: the request
        :param register: whether this is a register request (`True`)  or a deregister one (`False`)
        """
        # Expected arity is 1
        try:
            df_agt_description = msg.content[1]
        except IndexError:
            self.agent.send(
                refuse_message_from_request(
                    msg, "Missing argument: df agent description"
                )
            )
            return

        # Parameter type should be DFAgentDescription
        if not isinstance(df_agt_description, DFAgentDescription):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: df agent description, {df_agt_description}",
                )
            )
            return

        # Message is well formed, we can handle it
        self.agent.send(agree_message_from_request(msg))

        if register:
            # Agent must not be registered
            if df_agt_description.name in self.agent.storage:
                self.agent.send(failure_message_from_request(msg, "Already registered"))
                return

            # Everything is ok, we can process the registration
            self.agent.storage[df_agt_description.name] = df_agt_description
            self.agent.send(inform_message_from_request(msg, msg.content))
        else:
            # Agent must be registered
            if df_agt_description.name not in self.agent.storage:
                self.agent.send(failure_message_from_request(msg, "Not registered"))
                return

            # Everything is ok, we can process the deregister request
            del self.agent.storage[df_agt_description.name]
            self.agent.send(inform_message_from_request(msg, msg.content))

    async def _handle_search_request(self, msg: "ACLMessage") -> None:
        """
        Handle a search request.

        Message content must contains at least one parameter called df-agent-description and eventually another one
        called search-constraints. If the conditions are not met, then a REFUSE message is sent with the appropriate
        error class.

        Otherwise, two messages are sent: an AGREE, followed by an inform containing the result.

        This implementation doesn't support the federated DF feature for now. As a result, max-depth and search-id
        constraints are ignored.

        :param msg: message containing the search request
        """
        # At least the mandatory parameter df-agent-description
        if len(msg.content) < 2:
            self.agent.send(
                refuse_message_from_request(
                    msg, "Missing argument: df-agent-description"
                )
            )
            return

        # At most 2 parameters : df-agent-description and the optional parameter search-constraints
        if len(msg.content) > 3:
            self.agent.send(
                refuse_message_from_request(msg, "Unexpected argument count")
            )
            return

        # df-agent-description must be a DFAgentDescription
        if not isinstance(msg.content[1], DFAgentDescription):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: df-agent-description, {msg.content[1]}",
                )
            )
            return

        # If present, search-constraints parameter must be a SearchConstraints
        if len(msg.content) == 3 and not isinstance(msg.content[2], SearchConstraints):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: search-constraints, {msg.content[2]}",
                )
            )
            return

        # Everything is fine, we can handle the request
        self.agent.send(agree_message_from_request(msg))

        result = self._filter_descriptions(msg.content[1])

        # Constraint result
        if len(msg.content) == 3:
            constraints: "SearchConstraints" = msg.content[2]
            if constraints.max_results is not None:
                result = result[: constraints.max_results]

        self.agent.send(inform_message_from_request(msg, [msg.content, result]))

    async def _handle_modify_request(self, msg: "ACLMessage") -> None:
        """
        Handle a modify request.

        Expect one argument named df-agent-description of type :class:`DFAgentDescription` which is the new description
        for the sender agent. If an agent tries to modify the description of an other agent, a failure message will be
        sent.

        :param msg: modify request
        """
        # At least the mandatory parameter df-agent-description
        if len(msg.content) < 2:
            self.agent.send(
                refuse_message_from_request(
                    msg, "Missing argument: df-agent-description"
                )
            )
            return

        # At most 2 parameters : df-agent-description and the optional parameter search-constraints
        if len(msg.content) > 2:
            self.agent.send(
                refuse_message_from_request(msg, "Unexpected argument count")
            )
            return

        # df-agent-description must be a DFAgentDescription
        if not isinstance(msg.content[1], DFAgentDescription):
            self.agent.send(
                refuse_message_from_request(
                    msg,
                    f"Unrecognised parameter value: df-agent-description, {msg.content[1]}",
                )
            )
            return

        # Everything is fine, we can handle the request
        self.agent.send(agree_message_from_request(msg))

        # If sender is modifying description of another agent, failure
        if msg.content[1].name != msg.sender:
            self.agent.send(failure_message_from_request(msg, "Unauthorized"))
            return

        # If record doesn't exist, then failure
        if msg.content[1].name not in self.agent.storage:
            self.agent.send(failure_message_from_request(msg, "Not registered"))
            return

        # Otherwise perform the change
        self.agent.storage[msg.content[1].name] = msg.content[1]
        self.agent.send(inform_message_from_request(msg, msg.content))

    def _filter_descriptions(
        self, filter_description: "DFAgentDescription"
    ) -> List["DFAgentDescription"]:
        """
        Filter all registered descriptions given the filter.

        :param filter_description: filter against registered descriptions will be tested
        """
        return list(
            filter(
                lambda e: _match_description(e, filter_description),
                self.agent.storage.values(),
            )
        )


def _match_description(
    description: "DFAgentDescription", description_filter: "DFAgentDescription"
) -> bool:
    """
    Decide if the given `description` match the provided filter.

    :param description: description to be filtered
    :param description_filter: filter to test the description against
    :return: `True` if the description matches, `False` otherwise
    """
    return (
        (description_filter.name is None or description.name == description_filter.name)
        and (
            description_filter.services is None
            or set(description_filter.services) <= set(description.services)
        )
        and (
            description_filter.protocols is None
            or set(description_filter.protocols) <= set(description.protocols)
        )
        and (
            description_filter.ontologies is None
            or set(description_filter.ontologies) <= set(description.ontologies)
        )
        and (
            description_filter.languages is None
            or set(description_filter.languages) <= set(description.languages)
        )
        and (
            description_filter.lease_time is None
            or description_filter.lease_time == description.lease_time
        )
        and (
            description_filter.scope is None
            or description_filter.scope == description.scope
        )
    )


class ServiceDescription:
    """
    Description of each service registered with the DF.

    Available properties are:

    - **name**: name of the service
    - **type**: a string describing what kind of service it is. For example : "fipa-df"
    - **protocols**: protocols this agent supports. For example: "fipa-request"
    - **ontologies**: ontologies this agent understands. For example: "fipa-agent-management"
    - **languages**: languages this agent understands. For example: "fipa-sl0"
    - **ownership**: the owner of the service
    - **properties**: a set of properties

    It is part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        protocols: FrozenSet[str] = frozenset(),
        ontologies: FrozenSet[str] = frozenset(),
        languages: FrozenSet[str] = frozenset(),
        ownership: Optional[str] = None,
        properties: FrozenSet[Property] = frozenset(),
    ) -> None:
        self.name = name
        self.type = type
        self.protocols = protocols
        self.ontologies = ontologies
        self.languages = languages
        self.ownership = ownership
        self.properties = properties

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and (
            o.name == self.name
            and o.type == self.type
            and o.protocols == self.protocols
            and o.ontologies == self.ontologies
            and o.languages == self.languages
            and o.ownership == self.ownership
            and o.properties == self.properties
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.type,
                self.protocols,
                self.ontologies,
                self.languages,
                self.ownership,
                self.properties,
            )
        )


class DFAgentDescription:
    """
    Description that can be registered with the DF service.

    - **name**: :class:`AID` of the agent
    - **services**: A set of services this agent supports
    - **protocols**: A list of interaction protocols this agent supports
    - **ontologies**:  A list of ontologies this agent supports. For example: "fipa-agent-management"
    - **languages**: A list of languages (for example "fipa-sl0") this agent knows.
    - **lease-time**: The duration or time at which the lease for this registration will expire
    - **scope**: Visibility of the record. Can be either local or global (default is global)

    This object is part of the fipa-agent-management ontology. See http://fipa.org/specs/fipa00023/SC00023K.html.
    """

    def __init__(
        self,
        name: Optional[AID] = None,
        services: FrozenSet[ServiceDescription] = frozenset(),
        protocols: FrozenSet[str] = frozenset(),
        ontologies: FrozenSet[str] = frozenset(),
        languages: FrozenSet[str] = frozenset(),
        lease_time: Optional[datetime] = None,
        scope: str = "global",
    ) -> None:
        self.name = name
        self.services = services
        self.protocols = protocols
        self.ontologies = ontologies
        self.languages = languages
        self.lease_time = lease_time
        self.scope = scope

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and (
            o.name == self.name
            and o.services == self.services
            and o.protocols == self.protocols
            and o.ontologies == self.ontologies
            and o.languages == self.languages
            and o.lease_time == self.lease_time
            and o.scope == self.scope
        )


class SearchConstraints:
    """
    This object is used to constraint the results of a search (either in the AMS or DF).

    It contains the following fields:

    - **max_depth**: if the DF agent supports federation, use this parameter to limit the request propagation.
    - **max_results**: limit the number of results returned by the request
    - **search_id**: assign a globally unique identifier for this search request

    Part of the fipa-agent-management ontology, see http://fipa.org/specs/fipa00023/SC00023K.html
    """

    def __init__(
        self,
        max_depth: Optional[int] = None,
        max_results: Optional[int] = None,
        search_id: Optional[str] = None,
    ) -> None:
        self.max_depth = max_depth
        self.max_results = max_results
        self.search_id = search_id

    def __eq__(self, o: object) -> bool:
        return o is self or (
            isinstance(o, type(self))
            and o.max_depth == self.max_depth
            and o.max_results == self.max_results
            and o.search_id == self.search_id
        )
