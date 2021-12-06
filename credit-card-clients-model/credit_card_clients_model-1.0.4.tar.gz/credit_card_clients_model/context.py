"""Make context."""

import os
import click
import urllib.request
from pathlib import Path
from loguru import logger
from datetime import datetime
from credit_card_clients_model.config import config


@click.command(name="context")
@click.option("--context_dir", type=click.Path(writable=True), default=config.CONTEXT_DIR)
@click.option(
    "--date",
    type=click.STRING,
    default=datetime.now().strftime("%Y%m%d"),
    help="Date in format yyyymmdd [Current date]",
)
def context(context_dir: str, date: str) -> None:
    """Run processing scripts to grab data from SnowFlake database.

    It creates context files in ```<context_dir>/<date>```.
    """
    out_path = os.path.join(context_dir, date)
    logger.info("Fetching data ...")
    Path(out_path).mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(config.DATASET_URL, os.path.join(out_path, config.DATASET_FILENAME))
    logger.info("Completed!")


if __name__ == "__main__":
    context()
