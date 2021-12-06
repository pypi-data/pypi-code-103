"""Fetch data module."""

import urllib.request
from datetime import datetime
from pathlib import Path

import click
from loguru import logger

from modelchallangekleiner.utils.utils import DEFAULT_CONTEXT_PATH, DEFAULT_DATASET_URL


@click.command()
@click.option(
    "--date",
    type=click.STRING,
    default=datetime.now().strftime("%Y%m%d"),
    help="Date in format yyyymmdd [Current date]",
)
@click.option("--context_path", default=DEFAULT_CONTEXT_PATH)
@click.option("--dataset_url", default=DEFAULT_DATASET_URL)
def fetch_data_cli(date: str, context_path: str, dataset_url: str) -> None:
    """Fetch data from UCI url to train
    Parameters:
        :param date (str): date on the context files
        :param context_path (str): path to the context files
    """
    output_path = f"{context_path}/{date}"

    logger.info(f"Fetching data from {dataset_url}")

    try:
        # check if path exist and download dataset
        Path(output_path).mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(dataset_url, f"{output_path}/uci_dataset.xls")
        logger.info(f"Download complete. Path: {output_path}/uci_dataset.xls")

    except Exception as e:
        logger.error(f"Error ocurred: {e}")


if __name__ == "__main__":
    fetch_data_cli()
