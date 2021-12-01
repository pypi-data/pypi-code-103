# coding: utf-8
"""
This example shows heavy exchanges between agents.

One sender with a bunch of receivers. Time elapsed between sending and receiving is displayed.
"""
import time

import piaf.comm
import piaf.agent
import piaf.behavior

from typing import Sequence


class HeavySenderBehavior(piaf.behavior.Behavior):
    """
    Behavior for the sender agent.

    It builds a message containing the current time and send it to other agents.
    """

    def __init__(self, agent: "HeavySenderAgent"):
        super().__init__(agent)
        self.last_call = None

    async def action(self):
        msg = (
            piaf.comm.ACLMessage.Builder()
            .performative(piaf.comm.Performative.INFORM)
            .receiver(self.agent.receivers)
            .content(time.time_ns())
            .build()
        )
        self.agent.send(msg)

    def done(self):
        """Infinite behavior."""
        return False


class ReceiveBehavior(piaf.behavior.Behavior):
    """
    Behavior for receivers.

    It unpacks the content and displays how much time elapsed between the mesage
    creation and its processing.
    """

    async def action(self):
        msg = await self.agent.receive()
        tm = (time.time_ns() - msg.acl_message.content) / 1_000_000
        self.logger.info(
            "[%s] Msg received in %ims.",
            self.agent.aid.short_name,
            tm,
        )

    def done(self):
        """Infinite behavior."""
        return False


class HeavySenderAgent(piaf.agent.Agent):
    """
    Agent in charge of sending messages.

    You must pass a list of aids identifying the receivers.
    """

    def __init__(self, aid, platform, receivers: Sequence["piaf.comm.AID"]):
        """:param receivers: the receivers"""
        super().__init__(aid, platform)
        self.receivers = receivers

        self.add_behavior(HeavySenderBehavior(self))


class SimpleReceiverAgent(piaf.agent.Agent):
    """Receiver agent."""

    def __init__(self, aid, platform, *args, **kwargs):
        super().__init__(aid, platform, *args, **kwargs)

        self.add_behavior(ReceiveBehavior(self))


if __name__ == "__main__":
    import asyncio
    import logging
    import piaf.platform

    # Create and configure platform
    ap = piaf.platform.AgentPlatform("localhost")

    async def main():
        await ap.start()

        # Create a bunch of receivers
        receivers = []
        for i in range(100):
            receivers.append(
                await ap.agent_manager.create(SimpleReceiverAgent, f"rcv_{i}")
            )

        # Create one heavy sender
        sender = await ap.agent_manager.create(
            HeavySenderAgent, "sender", False, receivers
        )

        # Invoke agents
        for aid in receivers:
            await ap.agent_manager.invoke(aid)
        await ap.agent_manager.invoke(sender)

    # Configure logging to see things
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    # The program will run until you hit Ctrl+C
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(ap.stop())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
