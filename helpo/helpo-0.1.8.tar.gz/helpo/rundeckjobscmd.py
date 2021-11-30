import typer
import os
from helpo.rundeckjobs import RundeckJobs
from loguru import logger

app = typer.Typer()


@logger.catch
@app.command()
def search_uptimerobot(
        deployment_action: str = os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
        uptimerobot_api_key: str = os.environ.get("RD_OPTION_UPTIMEROBOT_API_KEY"),
        fqdn: str = os.environ.get("RD_OPTION_FQDN"),
        force_apply: bool = bool(os.environ.get('RD_OPTION_FORCE_APPLY'))
):
    rundeck_jobs = RundeckJobs()
    rundeck_jobs.search_uptimerobot(uptimerobot_api_key=uptimerobot_api_key, fqdn=fqdn,
                                    deployment_action=deployment_action, force_apply=force_apply)


if __name__ == "__main__":
    app()
