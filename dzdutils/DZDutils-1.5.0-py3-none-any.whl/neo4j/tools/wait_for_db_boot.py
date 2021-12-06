import time
import logging
import py2neo
from typing import Callable, Dict, List

log = logging.getLogger(__name__)


def wait_for_db_boot(
    neo4j: Dict = {}, timeout_sec: int = 120, log_func: Callable = print
):
    """[summary]

    Args:
        neo4j (Dict, optional): py2neo.Graph() properties as dict. Defaults to {}.
        timeout_sec (int, optional): How long do we want to wait in seconds. Defaults to 120.

    Raises:
        TimeoutError: [description]
    """

    timeout: float = time.time() + timeout_sec
    last_exception: Exception = None
    db_runs: bool = False
    log_func(f"Waiting {timeout_sec} seconds for neo4j@'{neo4j}' to boot up.")
    while not db_runs:
        try:
            g = py2neo.Graph(**neo4j)
            g.run("MATCH (n) RETURN n limit 1")
            log_func("Neo4j booted")
            db_runs = True
        except Exception as e:
            last_exception = e
            log_func(".")
            time.sleep(5)
        if time.time() > timeout:
            log_func(f"...neo4j@'{neo4j}' not booting up.")
            raise last_exception
