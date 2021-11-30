import os
import sys
import time
import glob
import json
import datetime
import string
import random
from pathlib import Path
import re
import logging
import importlib
import importlib.util
import traceback
from fk.batch.db import Database
import fk.utils
import fk.utils.Watchdog
from pprint import pformat

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_MS = 0.999


def random_token(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for i in range(length))


class BatchProcessor:
    def __init__(self, config):
        self.worker_id = random_token(10)
        self.config = config
        self.do_log = self.config.get("batch-log-logging", True)
        self.last_cleanup_time = datetime.datetime.now()
        self.task_filter = re.compile("^([0-9a-z\-_]+(\/[0-9a-z\-_]+)*)$")
        self.last_status_time = None
        self.callables = {}
        self.callables_params = {}
        self.entry_name = "batch_filter_entrypoint"
        self.param_name = "batch_filter_parameters"
        if self.config.get("db-hostname", "skip") == "skip":
            logger.warning("Skipping database initialization")
        else:
            self.db = Database(self.config)
        logger.info(f"Batch Processor {self.worker_id} instanciated")

    def __del__(self):
        logger.info(f"Batch Processor {self.worker_id} deleted")
        self.worker_id = None

    def verify(self):
        modules = self.list_modules()
        ok = []
        failed = []
        for (name, error) in modules:
            if error:
                failed.append((name, error))
            else:
                ok.append(name)
        if ok:
            logger.info("Available modules:")
            for name in ok:
                logger.info(f" + '{name}'")
        if failed:
            message = ""
            logger.info("Failed modules:")
            for (name, error) in failed:
                logger.error(f" + '{name}': {error}")
                message += f"{name}: {error}\n"
            return False, message
        logger.info(f"Extended logging={self.do_log}")
        return True, ""

    def load_module_by_filepath(self, module_name, module_filepath):
        module = None
        failure = None
        spec = None
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_filepath)
            spec.submodule_search_locations = list(__import__(__name__).__path__)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            failure = f"Import of module '{module_name}'from file '{module_filepath}' had errors ({e}). (Spec was {pprint.pformat(spec)})"
            module = None
        return module, failure

    def load_module_by_package(self, module_name, package_path=None):
        module = None
        failure = None
        try:
            module = importlib.import_module(module_name, package_path)
        except Exception as e:
            failure = f"Import of module '{module_name}'from package '{package_path}' had errors ({e})"
            module = None
        return module, failure

    def get_item_types(self):
        module_root_raw = self.config.get("batch-filter-root", "/tmp/inexistant")
        module_root_object = Path(module_root_raw).resolve(strict=False)
        module_root = module_root_object.as_posix()
        if not module_root:
            logger.warning("Module root was not set")
        if not os.path.exists(module_root):
            logger.warning(f"Module root '{module_root}' did not exist")
        logger.info(f"Looking for types in '{module_root}':")
        ret = {}
        for path_object in module_root_object.rglob("*.py"):
            path_object = path_object.resolve(strict=False)
            path = path_object.as_posix()
            if path_object.name.startswith("__"):
                logger.warning(f"Skipping invalid path {path}")
                continue
            if not path.startswith(module_root):
                logger.warning(f"Skipping invalid path {path}")
                continue
            path_difference = path[len(module_root) + 1 :]
            name = Path(path_difference).with_suffix("").as_posix()
            ret[name] = path
            logger.info(f"  Found {name} (from {path})")
        return ret

    def list_modules(self):
        module_root_raw = self.config.get("batch-filter-root", "/tmp/inexistant")
        module_root_object = Path(module_root_raw).resolve(strict=False)
        module_root = module_root_object.as_posix()

        ret = []
        failure = None
        if not module_root:
            ret.append(("module_root", f"Module root was not set"))
        elif not os.path.exists(module_root):
            ret.append(("module_root", f"Module root '{module_root}' did not exist"))
        else:
            files_objects = module_root_object.rglob("*.py")
            for file_object in files_objects:
                module_filepath = file_object.as_posix()
                if not module_filepath:
                    logger.warn(f"Not posix path: {file_object}")
                    continue
                if file_object.name.startswith("__"):
                    logger.warn(f"Skipping internal: {file_object}")
                    continue
                if fk.utils.file_contains_str(module_filepath, self.entry_name):
                    try:
                        module, failure = self.load_module_by_filepath(module_filepath, module_filepath)
                        if module:
                            if hasattr(module, self.entry_name):
                                entry_method = getattr(module, self.entry_name)
                                if not callable(entry_method):
                                    entry_method = None
                                    failure = f"Entrypoint was not callable in filter module {module_filepath}"
                            else:
                                failure = f"Filter module {module_filepath} did not have method {self.entry_name}"
                        else:
                            failure = f"Filter module {module_filepath} could not be loaded because: {failure}"
                    except Exception as e:
                        failure = f"Import of module '{module_filepath}' had errors and was skipped ({e})"
                else:
                    failure = f"No entrypoint found in filter module {module_filepath}"
                # logger.warn(f"Appending stat: {module_filepath}:{failure}")
                ret.append((module_filepath, failure))
        return ret

    def get_callable_for_type_raw(self, t):
        match = self.task_filter.match(t)
        module_name = None
        entry_method = None
        param_dict = None
        failure = None
        # Is this a match?
        if match:
            # Exctract the data we want
            module_name = match.group(1)
            module_filename = module_name + ".py"
            module_filepath = os.path.join(self.config.get("batch-filter-root", "/dev/null"), module_filename)
            module = None
            if os.path.exists(module_filepath):
                if fk.utils.file_contains_str(module_filepath, self.entry_name):
                    try:
                        module, failure = self.load_module_by_filepath(module_name, module_filepath)
                        if module:
                            if hasattr(module, self.entry_name):
                                entry_method = getattr(module, self.entry_name)
                                if not callable(entry_method):
                                    entry_method = None
                                    failure = f"Entrypoint was not callable in filter module {module_filepath}"
                                if hasattr(module, self.param_name):
                                    param_dict = getattr(module, self.param_name)
                            else:
                                failure = f"Filter module {module_filepath} did not have method {self.entry_name}"
                        else:
                            failure = f"Filter module {module_filepath} could not be loaded because: {failure}"
                    except Exception as e:
                        failure = f"Import of module '{module_name}' had errors and was skipped ({e})"
                else:
                    failure = f"No entrypoint found in filter module {module_filepath}"
            else:
                failure = f"Could not find filter module {module_filepath}"
        else:
            failure = f"No match for type {t}"
        return entry_method, param_dict, failure

    def get_callable_for_type(self, t):
        if t in self.callables:
            return self.callables.get(t), self.callables_params.get(t), None
        else:
            cb, params, failure = self.get_callable_for_type_raw(t)
            if cb:
                self.callables[t] = cb
            if params:
                self.callables_params[t] = params
            return cb, params, failure

    def _watchdog_hang_detected(self):
        logger.error("Watchdog triggered exception, restarting batch")
        sys.exit(99)

    def _execute_safely(self, entrypoint, params, item):
        # logger.info("SAFE EXECUTION STARTED!")
        failure = None
        result = None
        try:
            # We cap runtime at TTL from which ever is set first; item ttl, param ttl or environment fallback value
            timeout = self.config.get("batch-default-ttl", 0)
            timeout = params.get("ttl_seconds", timeout) if params else timeout
            timeout = item.get("ttl_seconds", timeout) if item else timeout
            if timeout and timeout > 0:
                logger.info(f"Using watchdog with ttl={timeout}sec")
                watchdog = fk.utils.Watchdog.Watchdog(timeout, self._watchdog_hang_detected)
            else:
                logger.info(f"No watchdog enabled")
            # logger.info("££££ Entry")
            unpackable = entrypoint(item, self.config)
            try:
                result, failure = unpackable
            except TypeError as te:
                failure = f"Filter did not return exactly one value and one error"
                logger.warning(failure)
                return None, failure
            # logger.info("££££ Exit")
        except fk.utils.Watchdog.Watchdog:
            logger.warning("Watchdog triggered exception")
            failure = f"Execution timed out after {timeout} seconds"
        except Exception as e:
            logger.warning("")
            logger.warning("")
            logger.warning(f"###############################################")
            logger.warning(f"#    Batch item: {item} on worker {self.worker_id}")
            logger.warning(f"# Failed with: {e} ({type(e).__name__}, {e.args})")
            failure = f"{e}  ({type(e).__name__}, {e.args})"
            logger.warning(f"#          At:")
            traceback.print_exc()
            logger.warning(f"#######################################")
            logger.warning("")
            logger.warning("")
        if None is not watchdog:
            watchdog.stop()
        # logger.info("SAFE EXECUTION FINISHED!")

        watchdog = None
        return result, failure

    def execute_one_batch_item(self):
        """
        Take ownership of one batch item and make sure it is properly executed and updated with status underway
        """
        item = self.db.book_batch_item(self.db.PENDING, self.db.IN_PROGRESS, self.worker_id)
        if item:
            if self.do_log:
                logger.info("Processing item:")
                logger.info(pformat(item))
            id = item.get("id", None)
            t = item.get("type", None)
            updated_at = item.get("updated_at", None)
            if id and t and updated_at:
                entrypoint, params, failure = self.get_callable_for_type(t)
                if entrypoint and failure:
                    entrypoint = None
                    failure = f"{failure} AND ENTRYPOINT WAS SET!"
                result = None
                if entrypoint:
                    result, failure = self._execute_safely(entrypoint, params, item)
                if failure:
                    logger.warning("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ BATCH FILTER FAILED WITH ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
                    logger.warning(failure)
                    logger.warning("")
                id2, updated_at2 = self.db.bump_batch_item(id=id, status=self.db.FAILED if failure else self.db.DONE, error=failure, updated_at=updated_at, result=result) or (None, None)
                if self.do_log:
                    logger.info(f"id2={id2}, updated_at2={updated_at2}, id={id}, updated_at={updated_at}")
                return True
            else:
                logger.warning(f"Missing data for item id={id}, type={t}, updated_at={updated_at}")
        # else:
        # logger.info(f"No pending items found")
        return False

    def execute_one_throttled_batch_item(self):
        """
        Take ownership of one batch item and make sure it is properly executed and updated with status underway
        NOTE: Throttled version
        """
        item = self.db.book_throttled_batch_item(self.db.PENDING, self.db.IN_PROGRESS, self.worker_id)
        if item:
            if self.do_log:
                logger.info("Processing throttled item:")
                logger.info(pformat(item))
            id = item.get("id", None)
            t = item.get("type", None)
            updated_at = item.get("updated_at", None)
            if id and t and updated_at:
                if item.get("wait_millis", 0) > 0:
                    logger.warning("Item not booked")
                    logger.warning(pformat(item))
                    failure = "Not booked"
                else:
                    entrypoint, params, failure = self.get_callable_for_type(t)
                    if entrypoint and failure:
                        entrypoint = None
                        failure = f"{failure} AND ENTRYPOINT WAS SET!"
                    result = None
                    if entrypoint:
                        result, failure = self._execute_safely(entrypoint, params, item)
                    if failure:
                        logger.warning("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ BATCH FILTER FAILED WITH ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
                        logger.warning(failure)
                        logger.warning("")
                id2, updated_at2 = self.db.bump_batch_item(id=id, status=self.db.FAILED if failure else self.db.DONE, error=failure, updated_at=updated_at, result=result) or (None, None)
                if self.do_log:
                    logger.info(f"id2={id2}, updated_at2={updated_at2}, id={id}, updated_at={updated_at}")
                return True
            else:
                logger.warning(f"Missing data for item id={id}, type={t}, updated_at={updated_at}")
        # else:
        # logger.info(f"No pending items found")
        return False

    # Make sure data is a string ready for insertion into db
    def _prepare_data(self, data):
        if data == None:
            return None
        data_type = type(data)
        if data_type is dict:
            data = json.dumps(data, indent=3, sort_keys=True, default=str)
        elif data_type is not str:
            data = str(data)
        return data

    def insert_batch_item(self, type="test", data=None, ttl_seconds=None, result=None, priority=50, source=None, throttle_key=None, throttle_limit=1, throttle_period=1):
        """
        Insert a new batch item into the database, ready for execution
        """
        data = self._prepare_data(data)
        # fmt: off
        return self.db.insert_batch_item(
            {
                "priority": priority,
                "ttl_seconds": ttl_seconds, 
                "data": data,
                "result": result,
                "type": type,
                "status": self.db.PENDING,
                "throttle_key": throttle_key,
                "throttle_limit": throttle_limit,
                "throttle_period": throttle_period,
                "source": source
            }
        )
        # fmt: on

    def _update_hang_status(self):
        self.db.update_batch_hang_status()

    def retry_hung_jobs(self):
        self.db.bump_batch_items(self.db.HUNG, self.db.PENDING)

    def delete_hung_jobs(self):
        self.db.delete_batch_items_with_status(self.db.HUNG)

    def delete_failed_jobs(self):
        self.db.delete_batch_items_with_status(self.db.FAILED)

    def delete_all_jobs(self):
        self.db.delete_all()

    def bump_job_by_id(self, id, status):
        self.db.bump_batch_item_status(id, status)

    def retry_job_by_id(self, id):
        self.db.bump_batch_item_status(id, self.db.PENDING)

    def delete_job_by_id(self, id):
        self.db.delete_by_id(id)

    def get_job_counts(self):
        raw = self.db.get_job_counts()
        out = {}
        totals = {}
        for row in raw:
            t = row.get("type")
            s = row.get("status")
            c = row.get("count")
            totals[s] = totals.get(s, 0) + c
            out[t] = out.get(t, {})
            out[t][s] = c
        out["total"] = totals
        return out

    def get_job_times(self):
        raw = self.db.get_job_times()
        return raw

    def get_worker_stats(self):
        raw = self.db.get_worker_stats()
        return raw

    def get_status(self):
        # fmt: off
        status = {
             "status": self.db.get_status_counts()
            , "counts": self.get_job_counts()
            , "times": self.get_job_times()
            , "workers": self.get_worker_stats()
        }
        # fmt: on
        return status

    def process(self):
        # Perform some cleanup on occation
        now = datetime.datetime.now()
        if now - self.last_cleanup_time > datetime.timedelta(seconds=CLEANUP_INTERVAL_MS):
            self.last_cleanup_time = now
            self._update_hang_status()
        # Try to process one item
        if not self.execute_one_throttled_batch_item():
            # Lets not get stuck in a loop!
            time.sleep(1)
