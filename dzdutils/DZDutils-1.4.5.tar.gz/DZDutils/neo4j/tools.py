from datetime import date
import time
import logging
import py2neo
import re
import math
from typing import Callable, Dict, List

log = logging.getLogger(__name__)


def wait_for_db_boot(neo4j: Dict = {}, timeout_sec=120, log_func: Callable = print):
    """[summary]

    Args:
        neo4j (Dict, optional): py2neo.Graph() properties as dict. Defaults to {}.
        timeout_sec (int, optional): How long do we want to wait in seconds. Defaults to 120.

    Raises:
        TimeoutError: [description]
    """

    timeout = time.time() + timeout_sec
    last_exception = None
    db_runs = False
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


def nodes_to_buckets_distributor(
    graph: py2neo.Graph,
    query: str,
    bucket_size: int = None,
    bucket_count: int = None,
    bucket_label_prefix: str = "BucketNo",
):
    """Supply a query returning nodes. These nodes will be distributed into sequences labels ("buckets")

    Args:
        graph (py2neo.Graph): [description]
        query (str): A query that is returning any node. The return param MUST be called `n` .e.g `Match (n:Person) return n`
        bucket_size (int, optional): Nodes per bucket. You will get a variable number of buckets of a fixed size
        bucket_count (int, optional): Counts of buckets; you will get a fixed number of buckets with a variable amount of nodes based on your query
        bucket_label_prefix (str, optional): [description]. Defaults to "BucketNo".
    Returns:
        [lst[str]]: Returns a list of str containing the generated label names
    """
    if bucket_size and bucket_count:
        raise ValueError(
            f"You can only set `bucket_size` or `bucket_count`. Not both at the same time. Got `bucket_size={bucket_size}` and `bucket_count={bucket_count}`"
        )
    elif bucket_count is None and bucket_size is None:
        raise ValueError(
            f"You have to set set `bucket_size` or `bucket_count`. Both are None at the moment."
        )
    if graph is None:
        graph = py2neo.Graph()
    node_count = 0
    if bucket_count:
        node_count = graph.run(
            f"CALL {{{query}}} return count(n) as cnt"
        ).to_data_frame()["cnt"][0]
        if node_count == 0:
            log.warning(f"No nodes found to seperate into buckets. Query '{query}' ")
            return []
        if node_count < bucket_count:
            log.warning(
                f"Only few nodes found ({node_count}) to seperate into buckets. Query '{query}' "
            )

        bucket_size = math.ceil(node_count / bucket_count)
        if bucket_size < 1:
            bucket_size = 1

    if bucket_size:
        iter_query: str = f"""
            CALL apoc.periodic.iterate(
            "CALL {{{query}}}
            WITH apoc.coll.partition(collect(n),{bucket_size}) as bucket_list
            WITH bucket_list, range(0, size(bucket_list)) AS bucket_count
            UNWIND bucket_count AS i
            return bucket_list[i] as bucket, i",
            "UNWIND bucket as n CALL apoc.create.addLabels(n,['{bucket_label_prefix}' + i]) YIELD node return count(*)",
            {{batchSize:1, parallel:true}})
            """
        res = graph.run(iter_query)

        if res.to_data_frame()["failedOperations"][0] != 0:
            raise ValueError(f"Bucketing failed: Cyper error message:\n{res}")
    # find and return the bucket labels.
    # todo: this is dirty. better would be to catch the return labels directly from the periodic query which is creating the labels. dk if possible atm
    labels = (
        graph.run(
            f'CALL db.labels() YIELD label WHERE label STARTS WITH "{bucket_label_prefix}" RETURN label'
        )
        .to_data_frame()
        .values.tolist()
    )

    match = re.compile(f"^{bucket_label_prefix}([0-9]*)$")
    return [
        label for label_list in labels for label in label_list if match.match(label)
    ]


class Neo4jPeriodicIterateError(Exception):
    pass


def run_periodic_iterate(
    graph: py2neo.Graph,
    cypherIterate: str,
    cypherAction: str,
    batchSize: int = None,
    parallel: bool = None,
    retries: int = None,
    batchMode: str = None,
    params: Dict = None,
    concurrency: int = None,
    failedParams: int = None,
    planner: str = None,
    _ignore_erros: bool = False,
    _only_return_query: bool = False,
):
    """
    https://neo4j.com/labs/apoc/4.1/overview/apoc.periodic/apoc.periodic.iterate/
    """
    args = locals()
    config_map = []
    for conf_key, conf_val in args.items():
        if conf_val and conf_key not in [
            "graph",
            "cypherIterate",
            "cypherAction",
            "_ignore_erros",
            "_only_return_query",
        ]:
            conf_val = (
                conf_val if not isinstance(conf_val, bool) else str(conf_val).lower()
            )
            config_map.append(f"{conf_key}:{conf_val}")
    query = f"""
    CALL apoc.periodic.iterate("{cypherIterate}","{cypherAction}",\n{{{",".join(config_map)}}}) 
    """
    log.debug(query)
    if _only_return_query:
        return query
    res = graph.run(query)
    res_data = res.to_data_frame()
    if res_data["failedOperations"][0] != 0 and not _ignore_erros:
        errors = []
        for error_msg, count in res_data["errorMessages"][0].items():
            errors.append(f"\n {error_msg}")
        raise Neo4jPeriodicIterateError(
            f'Error on {res_data["failedOperations"][0]} of {res_data["total"][0]} operations. Query: \n\n {query} \n\n ErrorMessages:\n{":".join(errors)}'
        )
    return res


def wait_for_fulltextindex_build_up(
    graph: py2neo.Graph,
    index_names: List[str],
    log_status_func: Callable = None,
    wait_time_sec: int = 1,
    timeout_sec: int = None,
):
    build_up = True
    if timeout_sec:
        timeout = time.time() + timeout_sec
    while build_up:
        indexes = graph.run(
            'SHOW INDEXES YIELD type, name, state WHERE type = "FULLTEXT"'
        ).to_data_frame()
        if not indexes.empty:
            indexes_online = []
            for index, db_index_data in indexes.iterrows():
                if (
                    db_index_data["name"] in index_names
                    and db_index_data["state"] == "ONLINE"
                ):
                    indexes_online.append(db_index_data["name"])
            build_up = bool(len(index_names) != len(indexes_online))
        if log_status_func:
            log_status_func(
                f"Indexes ONLINE: {indexes_online} WAITING: {list(set(index_names) - set(indexes_online))}"
            )
        if timeout_sec and time.time() > timeout:
            raise TimeoutError(
                f"Indexes {list(set(index_names) - set(indexes_online))} did not boot up in time."
            )
        time.sleep(wait_time_sec)
