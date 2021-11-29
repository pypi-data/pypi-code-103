"""Script to create DB tables."""
from models import Base
from sqlalchemy import create_engine

import os

PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = "5432"
PG_DB = os.getenv('PG_DB')
URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"


def main():
    """Program entrypoint."""
    engine = create_engine(URI, echo=True)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
