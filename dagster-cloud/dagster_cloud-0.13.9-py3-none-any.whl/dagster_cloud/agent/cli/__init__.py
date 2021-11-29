import uuid

from dagster.utils.interrupts import capture_interrupts
from dagster_cloud.agent.dagster_cloud_agent import DagsterCloudAgent
from dagster_cloud.instance import DagsterCloudAgentInstance
from typer import Typer

app = Typer()


@app.command()
def run():
    """Run the dagster-cloud agent."""
    with capture_interrupts():
        with DagsterCloudAgentInstance.get() as instance:
            if instance.is_ephemeral:
                raise Exception(
                    "dagster-cloud agent can't run using an in-memory instance. Make sure "
                    "the DAGSTER_HOME environment variable has been set correctly and that "
                    "you have created a dagster.yaml file there."
                )

            user_code_launcher = instance.user_code_launcher
            user_code_launcher.start()

            with DagsterCloudAgent() as agent:
                agent.run_loop(instance, user_code_launcher, agent_uuid=str(uuid.uuid4()))
