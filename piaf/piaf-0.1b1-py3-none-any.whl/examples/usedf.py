# coding: utf-8
"""
A small program testing the DF capabilities.

This module defines a service called :class:`FIPAWebService` which can send HTML pages from the `FIPA Website(http://fipa.org)`_
"""
import asyncio
from http.client import HTTPConnection, HTTPResponse

from piaf.agent import Agent
from piaf.behavior import Behavior
from piaf.service import DFAgentDescription, DFService, ServiceDescription
from piaf.comm import AID, MT_CONVERSATION_ID, ACLMessage, Performative
from piaf.platform import AgentPlatformFacade, AgentPlatform
from piaf.util import (
    FIPARequestProtocolBehavior,
    agree_message_from_request,
    inform_message_from_request,
    not_understood_message_from_request,
)


class FIPAWebPageService(Agent):
    """
    A service which sends the first 200 characters of FIPA website page.

    The service supports the FIPA Request protocol. The message content is expected to be the page path, in str format.
    """

    def __init__(self, aid: "AID", platform: "AgentPlatformFacade", *args, **kwargs):
        super().__init__(aid, platform, *args, **kwargs)

        # Initialize behaviors
        self.add_behavior(FIPAWebPageRequesProtocolBehavior(self))
        self.add_behavior(RegisterFIPAWebPageServiceBehavior(self))


class FIPAWebPageRequesProtocolBehavior(FIPARequestProtocolBehavior):
    """
    This behavior handle incoming request and retrieves the requested page.

    It supports the full Request Protocole and sends an Agree message before sending the Inform message.
    """

    def __init__(self, agent: "Agent", *args, **kwargs):
        """
        Initialize the behavior.

        It will create an HTTP connection to the FIPA website.
        """
        super().__init__(agent, *args, **kwargs)

        self.connection: "HTTPConnection" = HTTPConnection("fipa.org")
        self.lock = asyncio.Lock()

    def check_message(self, msg: "ACLMessage") -> bool:
        """
        Check if the given message is valid, i.e. the agent understands the content.

        If not, then replies with a NOT_UNDERSTOOD message with a reason.

        :param msg: message to check
        :rrturn: `True` if the message is valid, `False` otherwise.
        """
        if not isinstance(msg.content, str):
            self.agent.send(
                not_understood_message_from_request(
                    msg, "Content is expected to be an str value."
                )
            )
            return False
        return True

    async def on_valid_request(self, msg: "ACLMessage") -> None:
        """
        Behavior executed once we are sure the received message is valid.

        First it sends an AGREE message and then it uses an internal :class:`HTTPConnection` to request the
        the full page at the given path.

        :param msg: the valid message
        """
        self.agent.send(agree_message_from_request(msg))
        async with self.lock:
            response = self._retrieve_page(msg.content)
            self.agent.send(inform_message_from_request(msg, response.read(200)))
            response.read()  # Read all so we can re-use the connection for the next time. May take time.

    def _retrieve_page(self, url: "str") -> HTTPResponse:
        """
        Given a relative path, use the internal connection to the FIPA website to issue a GET request and return the received response.

        :param url: page path, starting with '/'.
        """
        self.connection.request("GET", url)
        return self.connection.getresponse()


class RegisterFIPAWebPageServiceBehavior(Behavior):
    """
    A one-shot behavior which registers our :class:`FIPAWebPageService` to the DF agent.
    """

    async def action(self) -> None:
        register_msg = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .conversation_id("fipa-web-page-service")
            .receiver(AID(f"DF@{self.agent.aid.hap_name}"))
            .content(
                [
                    DFService.REGISTER_FUNC,
                    DFAgentDescription(
                        self.agent.aid,
                        services=frozenset(
                            {
                                ServiceDescription(
                                    "Fipa web page service",
                                    protocols=frozenset({"fipa-request"}),
                                )
                            }
                        ),
                        protocols={"fipa-request"},
                    ),
                ]
            )
            .build()
        )

        self.agent.send(register_msg)


class TestingAgent(Agent):
    """
    A testing agent requesting the FIPA00023 specification.
    """

    def __init__(self, aid: "AID", platform: "AgentPlatformFacade", *args, **kwargs):
        super().__init__(aid, platform, *args, **kwargs)

        self.add_behavior(AskFIPA00023Behavior(self))


class AskFIPA00023Behavior(Behavior):
    """
    Request the FIPA00023 specification page to the first FIPA web service found.

    It uses the DF agent to search an agent providing the service and if such agent exists, it then sends a
    request to retrieve the page.
    """

    PAGE = "/specs/fipa00023/SC00023K.html"
    FIND_CONV = "find-fipa-web-page-service"
    ASK_CONV = "ask-page-fipa00023"

    def __init__(self, agent: "Agent", *args, **kwargs):
        super().__init__(agent, *args, **kwargs)
        self.is_done = False

    def done(self) -> bool:
        return self.is_done

    async def action(self) -> None:
        # Find FIPAWebPageService
        find = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .conversation_id(self.FIND_CONV)
            .receiver(AID(f"DF@{self.agent.aid.hap_name}"))
            .content(
                [
                    DFService.SEARCH_FUNC,
                    DFAgentDescription(
                        services=frozenset(
                            {
                                ServiceDescription(
                                    "Fipa web page service",
                                    protocols=frozenset({"fipa-request"}),
                                )
                            }
                        ),
                    ),
                ]
            )
            .build()
        )
        self.agent.send(find)

        # Wait until we get the response
        _ = await self.agent.receive(MT_CONVERSATION_ID(self.FIND_CONV))
        response = await self.agent.receive(MT_CONVERSATION_ID(self.FIND_CONV))

        # Extract service aid
        # According to DF spect, content is a tuple (request content, reponse)
        # The response is a list of matching agents, we take the first one
        if len(response.acl_message.content[1]) == 0:
            self.agent.logger.info("Service not available yet.")
            return
        service_aid = response.acl_message.content[1][0].name
        self.is_done = True

        # Contact service and ask page
        ask = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .conversation_id(self.ASK_CONV)
            .receiver(service_aid)
            .content(self.PAGE)
            .build()
        )
        self.agent.send(ask)

        # Wait until we get the response
        _ = await self.agent.receive(MT_CONVERSATION_ID(self.ASK_CONV))
        response = await self.agent.receive(MT_CONVERSATION_ID(self.ASK_CONV))

        # Display the first 200 chars
        self.agent.logger.info(
            f"[{self.agent.aid.short_name}]: {response.acl_message.content}"
        )


async def main(ap: "AgentPlatform"):
    """
    Start the platform, the DF agent and our agents

    :param ap: platform to start
    """
    # Start the platform
    await ap.start()

    # Add DF agents
    df_aid = await ap.agent_manager.create(DFService, "DF", True)
    await ap.agent_manager.invoke(df_aid)

    # Start the service.
    service_aid = await ap.agent_manager.create(FIPAWebPageService, "FIPAService")
    await ap.agent_manager.invoke(service_aid)

    # Start our testing agents
    for i in range(10):
        testin_aid = await ap.agent_manager.create(TestingAgent, f"testing-{i}")
        await ap.agent_manager.invoke(testin_aid)


if __name__ == "__main__":
    import logging

    # Configure logging level and handler to see things
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    # Create and start the platform
    ap = AgentPlatform("localhost")

    # We are using asyncio library to run our example
    # The program will run until you hit Ctrl+C
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main(ap))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(ap.stop())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
