import pprint
import logging
import os

from fk.db.DatabaseConnection import DatabaseConnection
from urllib.parse import urlparse, urlunparse, ParseResult

logger = logging.getLogger(__name__)

# fmt: off
configs={
    "empty:":(
        {}
        ,""
        ,""
    )
    , "hello:":(
        {
            "db-hostname":"hello.com"
            ,"db-port":1234
            ,"db-username":"arnold"
            ,"db-password":"secret123"
            ,"db-database":"mydb"
        }
        ,"F12F52B73358C297F47A80768ABDFADF20D021F6A20E9929178908F981B75FA1"
        ,"postgres://arnold:secret123@hello.com:1234/mydb"
    )
}
# fmt: on


def test_true():
    logger.info("Dummy unit test")
    return True


def test_db_get_config_hash():

    for name, pack in configs.items():
        logger.info(f"NAME:{name}")
        config, expected, _ = pack
        logger.info(f"config:{config}")
        logger.info(f"expected:{expected}")
        actual = DatabaseConnection.get_config_hash(config)
        logger.info(f"actual:{actual}")
        assert actual == expected
    return True


def test_db_url_to_and_from_config():
    for name, pack in configs.items():
        logger.info(f"NAME:{name}")
        expected_config, _, expected_url = pack
        logger.info(f"expected_config:{expected_config}")
        logger.info(f"expected_url:   {expected_url}")
        actual_url = DatabaseConnection.config_to_url(expected_config)
        actual_config = DatabaseConnection.url_to_config(expected_url)
        assert actual_url == expected_url
        assert actual_config == expected_config


def _test_db_get_same_twice():
    # fmt: off
    config= {
        "db-hostname":"hello.com"
        ,"db-port":"1234"
        ,"db-username":"arnold"
        ,"db-password":"secret123"
        ,"db-database":"mydb"
    }
    # fmt: on
    db1 = DatabaseConnection.get_connection(config)
    db2 = DatabaseConnection.get_connection(config)
    assert db1 == db2
