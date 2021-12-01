# coding: utf-8
"""
A simple module that demonstrate how to create a simple agent and a simple behavior.

This module defines:

 * An agent, called CustomAgent
 * One behavior, called HelloWorldBehavior
 * It also show how to launch the platform.
"""
import piaf.agent as agent

from piaf.behavior import Behavior


class HelloWorldBehavior(Behavior):
    """A behavior that uses the agent's logger to display an Hello World message."""

    async def action(self):
        """Body of the Behavior."""
        self.agent.logger.info("Hello world from HelloWorldBehavior !")


class CustomAgent(agent.Agent):
    """A simple agent using the the :class:`HelloWorldBehavior`."""

    def __init__(self, aid, platform):
        """Create a new agent and add the behavior."""
        super().__init__(aid, platform)

        # Create an instance of HelloWorldBehavior and add it to the agent
        b = HelloWorldBehavior(self)
        self.add_behavior(b)


if __name__ == "__main__":
    import asyncio
    import logging
    import piaf.platform as platform

    # Configure logging level and handler to see things
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    # Create agent platform
    ap = platform.AgentPlatform("localhost")

    async def main():
        """Coroutine that starts the platform and add agents."""
        # Before adding our agent, we need to start the platform. This ensure that the
        # AMS agent is created
        await ap.start()

        # Now we can add our agent
        aid = await ap.agent_manager.create(CustomAgent, "hello")
        await ap.agent_manager.invoke(aid)

    # We are using asyncio library to run our example
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
