import click
import re

from ocean import code
from ocean.main import Environment
from ocean.utils import sprint, PrintType, api_health_check


@click.command()
@click.option("--url", default="http://ocean-backend-svc:8000", help="pass backend url")
def cli(url):
    ctx = Environment(load=False)

    # make .oceanrc on home-dir and init
    if not ctx.config_path.exists():
        ctx.config_path.parent.mkdir(exist_ok=True)
        ctx.config_path.touch()

    # ip only: add default port
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", url):
        url += ":32080"
    # ip, port only: add 'http://'
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$", url):
        url = "http://" + url

    if api_health_check(url):
        # save env
        ctx.update_config(code.OCEAN_URL, url)
        ctx.update_config("presets", [])

        sprint("Setup Success.", PrintType.SUCCESS)
