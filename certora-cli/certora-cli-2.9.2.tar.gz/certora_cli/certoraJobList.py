import os.path
from datetime import datetime
from shutil import copyfile
from typing import Any, Dict, Optional

from certora_cli.certoraUtils import debug_print_, get_certora_root_directory, print_warning, read_json_file, remove_file, \
    write_json_file, print_error, abs_posix_path
from certora_cli.certoraUtils import RECENT_JOBS_FILE
import click
import sys
import requests
import time


class JobList:
    """
    Represents Recently executed jobs

    Structure is as follows:
    {
        "path_to_test/working_dir": [
            {
                "job_id": {JOB_ID},
                "output_url": {REPORT_URL: https://{DOMAIN}/output/.../data.json...},
                "notify_msg": {OPTIONAL: NOTIFICATION_MSG}
            },...
        ],...
    }

    Each path has a (FIFO) queue of up to {MAX_LENGTH} recently executed jobs
    The first element in the queue is the most recent one

    """

    jobs = {}  # type: Dict[str, Any]

    MAX_LENGTH = 10

    recent_jobs_path = ""
    temp_file_path = ""

    def __init__(self, current_path: str = os.getcwd(), debug: bool = False):
        self.current_path = abs_posix_path(current_path)
        self.debug = debug
        self.recent_jobs_path = os.path.join(get_certora_root_directory(), RECENT_JOBS_FILE)
        self.temp_file_path = os.path.join(get_certora_root_directory(), f".tmp{RECENT_JOBS_FILE}")
        self.get_recent_jobs(self.recent_jobs_path)

    def add_job(self, job_id: str, output_url: str, notify_msg: str, domain: str, user_id: str,
                anonymous_key: str) -> None:
        if not self.current_path:
            debug_print_(f"Current path attribute is missing. Skipped adding job {job_id} to recent jobs list",
                         self.debug)
            return
        new_job = {
            "anonymous_key": anonymous_key,
            "domain": domain,
            "job_id": job_id,
            "notify_msg": notify_msg,
            "output_url": output_url,
            "time": int(time.time()),
            "user_id": user_id
        }  # type: Dict[str, Any]
        try:
            if self.current_path not in self.jobs.keys():
                self.jobs[self.current_path] = []
            self.jobs[self.current_path].insert(0, new_job)  # insert at the front of the list
            if len(self.jobs[self.current_path]) > self.MAX_LENGTH:
                self.remove_oldest_job()
        except AttributeError as e:
            debug_print_(f"Couldn't add job {job_id}. Recent jobs file format may have changed: {e}", self.debug)
            self.rename_recent_jobs_file()

    def remove_oldest_job(self) -> None:
        if not self.current_path:
            debug_print_("Current path attribute is missing", self.debug)
            return
        if len(self.jobs[self.current_path]):
            removed_job = self.jobs[self.current_path].pop()  # remove the last element
            debug_print_(f"Removed job {removed_job.get('jobId', '')} from recent jobs list", self.debug)

    def remove_jobs_in_current_path(self) -> bool:
        if not self.current_path:
            print_error("Current path attribute is missing")
            return False

        self.jobs[self.current_path] = []
        return True

    def get_latest_job(self) -> Optional[Dict[str, Any]]:
        if not self.current_path:
            print_error("Current path attribute is missing")
            return None

        if self.current_path not in self.jobs:
            print_error(f"Current path {self.current_path} is not in jobs")
            return None

        return max(self.jobs[self.current_path], key=lambda job: 0 if "time" not in job else job["time"])

    def get_data(self) -> Dict[str, Any]:
        return self.jobs

    def save_data(self) -> None:
        # backup
        succeeded = self.copy(self.recent_jobs_path, self.temp_file_path)
        if not succeeded:
            debug_print_("Couldn't create a backup file.", self.debug)

        try:
            write_json_file(self.get_data(), self.recent_jobs_path)
            # remove the backup file
            remove_file(self.temp_file_path)
        except (ValueError, OSError) as e:
            debug_print_(f"Error occurred when saving json data: {e}", self.debug)
            self.revert()

    def save_recent_jobs_to_path(self, path: str = os.getcwd()) -> None:
        """
        Saves the ten last recent runs from a specific path (if exist) in that path.
        For example, if we run the tool from C:/Users/uri/Projects/EVMVerifier/Test/Bank
        We will save in file C:/Users/uri/Projects/EVMVerifier/Test/Bank/.certora_recent_jobs.json:

        {
            "workingDir": "C:/Users/uri/Projects/EVMVerifier/Test/Bank",
            "recentJobs": [
                {
                    "anonymous_key": "cdc45f5ee2e5e529db67c4f2ef969b46f758c80b",
                    "domain": "https://prover.certora.com",
                    "job_id": "8e05726cfa0ed98505bc",
                    "notify_msg": "",
                    "output_url": "https://prover.certora.com/output/53342/8e057...8505bc?anonymousKey=cdc45f5...",
                    "time": 1634060491,
                    "user_id": "53342"
                }
                ...
            ]
        }
        :param path: The path at which we will generate the file
        """
        path = abs_posix_path(path)
        all_data = self.get_data()
        recent_jobs_file_path = abs_posix_path(os.path.join(path, RECENT_JOBS_FILE))
        if path not in all_data:
            debug_print_(f"Couldn't create a recent jobs file for {path}.", self.debug)
            debug_print_(f"All data keys = {all_data.keys()}.", self.debug)
        else:
            path_data = \
                {
                    "workingDir": path,
                    "recentJobs": all_data[path]
                }

            if os.path.exists(recent_jobs_file_path):
                # backup

                succeeded = self.copy(recent_jobs_file_path, self.temp_file_path)
                if not succeeded:
                    debug_print_("Couldn't create a backup file.", self.debug)

            try:
                write_json_file(path_data, recent_jobs_file_path)
                # remove the backup file
                remove_file(self.temp_file_path)
            except (ValueError, OSError) as e:
                debug_print_(f"Error occurred when saving json data: {e}", self.debug)
                self.revert()

    def revert(self) -> None:
        """
        used when recent job file is corrupted
        overrides this file with the backup file (if exists)
        """
        if os.path.isfile(self.temp_file_path):
            succeeded = self.copy(self.temp_file_path, self.recent_jobs_path)
            if succeeded:
                # remove the backup file
                remove_file(self.temp_file_path)
        else:
            debug_print_("Couldn't revert recent jobs changes. Backup file does not exist", self.debug)

    def get_recent_jobs(self, file_path: str) -> None:
        """
        Sets the jobs attribute to be the JSON object stored in the supplied file_path
        If file_path format is wrong (on ValueError) renames the file
        """
        try:
            recent_jobs = read_json_file(file_path)
            self.jobs = recent_jobs
        except FileNotFoundError:
            debug_print_(f"Couldn't find recent jobs file in {file_path}", self.debug)
        except ValueError:
            debug_print_("Recent jobs file has incorrect format", self.debug)
            self.rename_recent_jobs_file()

    def copy(self, src_path: str, dst_path: str) -> bool:
        try:
            copyfile(src_path, dst_path)
            return True
        except OSError as e:
            debug_print_(f"Couldn't copy {src_path}: {e}", self.debug)
        return False

    def rename_recent_jobs_file(self) -> None:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        name = os.path.join(get_certora_root_directory(), f".incompatible.{current_time}{RECENT_JOBS_FILE}")
        try:
            os.rename(self.recent_jobs_path, name)
            print_warning(f"Recent jobs file was renamed. Please, see {name}")
        except (OSError, FileExistsError) as e:
            debug_print_(f"Couldn't rename the recent jobs file: {e}", self.debug)

    def get_asset_url_from_last_job(self, asset: str) -> Optional[str]:
        latest_job = self.get_latest_job()
        if latest_job is None:
            return None
        domain = latest_job.get("domain", None)
        job_id = latest_job.get("job_id", None)
        user_id = latest_job.get("user_id", None)
        anonymous_key = latest_job.get("anonymous_key", None)
        if domain is None or job_id is None or user_id is None or anonymous_key is None:
            return None
        url = f"{domain}/output/{user_id}/{job_id}/{asset}?anonymousKey={anonymous_key}"
        return url


def download_asset(url: Optional[str], asset_name: str) -> bool:
    if url is None:
        print_error(f"Failed to get url for {asset_name}")
        return False

    try:
        with requests.get(url, stream=True, timeout=10) as r:
            if r.status_code == requests.codes.ok:
                with open(asset_name, 'wb+') as downloaded_file:
                    for chunk in r.iter_content(chunk_size=8192):
                        downloaded_file.write(chunk)
                return True
            else:
                print_error(f"Got error {r.status_code} when getting {url}")
                return False
    except (requests.exceptions.Timeout, requests.exceptions.RequestException, ConnectionError):
        print_error(f"Could not download {url}")
        return False


@click.command()
@click.option("--clear", type=click.BOOL, default=False, help="clear recent jobs")
@click.option("--get_last", type=click.STRING, help="download asset from most recent job")
def main(clear: bool, get_last: Optional[str]) -> None:
    if clear and get_last is not None:
        print_error("Could not use both --clear and --get_last")
        sys.exit(1)
    if not clear and get_last is None:
        print_error("At least one option must be selected")
        sys.exit(1)

    result = True
    job_list = JobList()
    if clear:
        result = job_list.remove_jobs_in_current_path()
        if result:
            job_list.save_data()

    if get_last is not None:
        asset_name = get_last
        url = job_list.get_asset_url_from_last_job(asset_name)
        result = download_asset(url, asset_name)
    if not result:
        sys.exit(1)


if __name__ == '__main__':
    main()
