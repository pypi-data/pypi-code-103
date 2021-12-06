import os
import click
import pickle
import pandas as pd
from loguru import logger
from datetime import datetime
from sklearn.model_selection import train_test_split

from credit_card_clients_model.pipeline import pipeline
from credit_card_clients_model.config import config


@click.command(name="train")
@click.option("--context_dir", type=click.Path(writable=True), default=config.CONTEXT_DIR)
@click.option(
    "--date",
    type=click.STRING,
    default=datetime.now().strftime("%Y%m%d"),
    help="Date in format yyyymmdd [Current date]",
)
def train(context_dir: str, date: str) -> None:
    """Train the model."""

    logger.info("reading training data")
    data = pd.read_excel(
        os.path.join(context_dir, date, config.DATASET_FILENAME),
        skiprows=[0],
        # index_col=0,
    )

    X_train, X_test, y_train, y_test = train_test_split(
        data[config.FEATURES],
        data[config.TARGET],
        test_size=.2,
    )

    logger.info("training model")
    pipeline.fit(X_train, y_train)

    score = pipeline.score(X_test, y_test)
    logger.info(f"model score = {score}")

    logger.info("saving trained model")
    with open(os.path.join(config.MODELS_DIR, config.MODEL_FILENAME), "wb") as f:
        pickle.dump(pipeline, f)


if __name__ == "__main__":
    train()
