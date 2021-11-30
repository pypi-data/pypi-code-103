import typer
import os
from helpo.rundeckjobs import RundeckJobs
from loguru import logger

app = typer.Typer()


@logger.catch
@app.command()
def search_uptimerobot(
        deployment_action=os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
        uptimerobot_api_key=os.environ.get("RD_OPTION_UPTIMEROBOT_API_KEY"),
        fqdn=os.environ.get("RD_OPTION_FQDN"),
        force_apply=os.environ.get('RD_OPTION_FORCE_APPLY')
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.search_uptimerobot(uptimerobot_api_key, fqdn, deployment_action, force_apply)


if __name__ == "__main__":
    app()
