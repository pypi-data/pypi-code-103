from logging import getLogger
from typing import Iterable

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from monutils.db import connect

from monutils.args import CopyArgParser

logger = getLogger(__name__)


def dummy_tqdm(iterable: Iterable, *_, **kwargs) -> Iterable:
    return iterable


def copy(from_client: MongoClient, to_client: MongoClient, from_database: str, to_database: str,
         from_collection: str, to_collection: str, ignore_errors: bool = False) -> None:
    """ Copy a MongoDB collection to another.

    :param from_client: The source MongoDB client.
    :param to_client: The target MongoDB client.
    :param from_database: The source database.
    :param to_database: The target database.
    :param from_collection: The source collection.
    :param to_collection: The target collection.
    :param ignore_errors: If activate, ignore copy errors.
    """
    try:
        from dbtqdm.mongo import tqdm
    except ImportError:
        logger.warning('db-tqdm is not installed. If you want a progress bar, please install db-tqdm:\n\n'
                       'pip install db-tqdm>=1.1.3,<2.0')
        tqdm = dummy_tqdm
    from_collection = from_client[from_database][from_collection]
    to_collection = to_client[to_database][to_collection]
    total = from_collection.count_documents({})
    errors = 0
    for obj in tqdm(from_collection.find({}), desc='Copying', total=total):
        del obj['_id']
        try:
            to_collection.insert_one(obj)
        except DuplicateKeyError as e:
            if not ignore_errors:
                raise e
            errors += 1
    logger.warning(f'{errors} ignored errors:\n  Duplicates:{errors}')


def main() -> None:
    """ Main function. """
    args = CopyArgParser()
    from_client = connect(args.from_host, args.from_port, args.from_replicaset, args.from_user, args.from_password,
                          args.from_cert, args.from_ca, args.from_session_token, args.from_mode)
    to_client = connect(args.to_host, args.to_port, args.to_replicaset, args.to_user, args.to_password,
                        args.to_cert, args.to_ca, args.to_session_token, args.from_mode)
    from_db, to_db = args.from_database, args.to_database
    copy(from_client, to_client, from_db, to_db, args.from_collection, args.to_collection, args.ignore)


if __name__ == '__main__':
    main()
