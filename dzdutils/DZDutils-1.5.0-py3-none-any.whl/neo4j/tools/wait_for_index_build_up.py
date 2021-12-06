import py2neo
import time
from typing import Dict, List, Callable


def wait_for_index_build_up(
    graph: py2neo.Graph,
    index_names: List[str],
    log_status_func: Callable = None,
    wait_time_sec: int = 1,
    timeout_sec: int = None,
):
    # replace with db.awaitIndexes?
    build_up = True
    if timeout_sec:
        timeout = time.time() + timeout_sec
    while build_up:
        indexes = graph.run("SHOW INDEXES YIELD type, name, state").to_data_frame()
        if not indexes.empty:
            indexes_online = []
            for index, db_index_data in indexes.iterrows():
                if (
                    db_index_data["name"] in index_names
                    and db_index_data["state"] == "ONLINE"
                ):
                    indexes_online.append(db_index_data["name"])
                elif (
                    db_index_data["name"] in index_names
                    and db_index_data["state"] == "FAILED"
                ):
                    raise IndexError(f"'{db_index_data['name']}' has status FAILED.")
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
