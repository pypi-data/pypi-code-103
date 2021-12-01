# coding: utf-8
"""
A small program testing the AMS capabilities.

The scenario is the following:

1. Two agents are created
2. The first one perform a request to find active agents
3. It sends a `Hello World` message to inform agents of its presence

"""
import asyncio
import logging
from typing import Union
from piaf.agent import Agent, AgentState
from piaf.service import AMSService, AMSAgentDescription
from piaf.platform import AgentPlatform, AgentPlatformFacade
from piaf.comm import ACLMessage, Performative, AID
from piaf.behavior import Behavior


class SendHello(Behavior):
    """
    One shot behavior to say hello to all active agents.

    Use the AMS to search active agents and send an `INFORM` message.
    """

    async def action(self) -> None:
        """
        Behavior `action` method.

        1. Contact AMS and ask all active agents
        2. If AMS respond with INFORM
            1. Loop over received :class:`AMSAgentDescription` objects
            2. If neither owner nor the AMS, send hello

        """
        # First, create a message to query the AMS
        msg = (
            ACLMessage.Builder()
            .performative(Performative.REQUEST)
            .receiver(AID(f"ams@{self.agent.aid.hap_name}"))
            .conversation_id(f"{self.agent.aid.name}-sendhello")
            .content(
                [
                    AMSService.SEARCH_FUNC,
                    AMSAgentDescription(None, None, AgentState.ACTIVE),
                ]
            )
            .build()
        )
        self.agent.send(msg)

        # Wait a reply
        # If it succeeded, loop over content
        reply = await self.agent.receive()
        if reply.acl_message.performative == Performative.INFORM:
            content = reply.acl_message.content

            for agt_description in content:
                other_aid = agt_description.name

                # If the description is neither agent nor the AMS, send hello !
                if other_aid != self.agent.aid and other_aid.short_name != "ams":
                    self.agent.send(
                        ACLMessage.Builder()
                        .performative(Performative.INFORM)
                        .receiver(other_aid)
                        .conversation_id(
                            f"{self.agent.aid.name}-sendhello-{other_aid.name}"
                        )
                        .content("Hello friend!")
                        .build()
                    )


class DisplayReceivedMessage(Behavior):
    """One shot behavior displaying the first received message."""

    async def action(self) -> None:
        """Use the agent's logger to display the first received message."""
        msg = await self.agent.receive()
        self.agent.logger.info(
            f"From {msg.acl_message.sender}: {msg.acl_message.content}"
        )


class BroadcastAgent(Agent):
    """
    Simple agent broadcasting a 'Hello' message to other active agents.

    The broadcast is performed when the agent is invoked. Agent dies immediately after.
    """

    def __init__(
        self,
        aid: "AID",
        platform: "Union[AgentPlatformFacade, AgentPlatform]",
        *args,
        **kwargs,
    ):
        super().__init__(aid, platform, *args, **kwargs)

        self.add_behavior(SendHello(self))


class DisplayAgent(Agent):
    """A simple agent displaying the first received message and dying right after that."""

    def __init__(
        self,
        aid: "AID",
        platform: "Union[AgentPlatformFacade, AgentPlatform]",
        *args,
        **kwargs,
    ):
        super().__init__(aid, platform, *args, **kwargs)

        self.add_behavior(DisplayReceivedMessage(self))


async def main(ap: "AgentPlatform"):
    """
    Start the platform, add a bunch of agents.

    :param ap: platform to start
    """
    # Start the platform
    await ap.start()

    # Add some agents
    for i in range(10):
        aid = await ap.agent_manager.create(DisplayAgent, f"DA-{i}")
        await ap.agent_manager.invoke(aid)

    # Sleep a bit
    await asyncio.sleep(2)

    # Start the broadcast agent.
    aid = await ap.agent_manager.create(BroadcastAgent, "BA")
    await ap.agent_manager.invoke(aid)


if __name__ == "__main__":
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
