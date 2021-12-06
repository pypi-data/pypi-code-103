"""Train module"""
from datetime import datetime

import click
import pickle
import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split

from modelchallangekleiner.features.transformer import get_pipeline
from modelchallangekleiner.utils.utils import (
    DEFAULT_CONTEXT_PATH,
    DEFAULT_OUTPUT_PATH,
    FEATURES,
    TARGET,
)


@click.command()
@click.option(
    "--date",
    type=click.STRING,
    default=datetime.now().strftime("%Y%m%d"),
    help="Date in format yyyymmdd [Current date]",
)
@click.option("--context_path", default=DEFAULT_CONTEXT_PATH)
@click.option("--output_model_path", default=DEFAULT_OUTPUT_PATH)
def train_cli(date: str, context_path: str, output_model_path: str):
    """Train model
    Parameters:
        :param date (str): date for the context files
        :param context_path (str): path to the context files
    """

    output_path = f"{context_path}/{date}"

    df = pd.read_excel(
        f"{output_path}/uci_dataset.xls",
        skiprows=[0] if date != "test_dataset" else None,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET], test_size=0.20
    )

    pipeline = get_pipeline()

    logger.info("Training model..")

    try:
        pipeline.fit(X_train[FEATURES], y_train)

        # save training model as object
        with open(f"{output_model_path}/model.pkl", "wb") as f:
            pickle.dump(pipeline, f)

        score = pipeline.score(X_test, y_test)
        logger.info(
            f"Training success! model score: {score}. Model saved at {output_model_path}/model.pkl"
        )

    except Exception as e:
        logger.error(f"Error ocurred. {e}")


if __name__ == "__main__":
    train_cli()
