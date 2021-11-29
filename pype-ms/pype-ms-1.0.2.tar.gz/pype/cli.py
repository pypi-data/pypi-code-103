import datetime
import importlib
import logging
import os
import pprint
import socket
import sys
import traceback

import click
import yaml
from pype import utils

logging.basicConfig(level=logging.INFO)


class Status:
    def __init__(self, dir_):
        self.dir = dir_
        self.status = "status"
        for status in ["Done", "Failed", "Running"]:
            if os.path.exists(os.path.join(dir_, status)):
                self.status = status

        self.status_path = os.path.join(dir_, self.status)


    def done(self):
        self._set_status("Done")

    def running(self):
        self._set_status("Running")

    def failed(self):
        self._set_status("Failed")

    def _set_status(self, status):
        timestamp = datetime.datetime.now().strftime("%y/%m/%d-%H:%M:%S")

        if not os.path.exists(self.status_path):
            with open(self.status_path, "w") as f:
                f.write("Host: " + socket.gethostname() + "\n")

        with open(self.status_path, "a") as status_file:
            status_file.write(status + ": " + timestamp + "\n")

        status_path = os.path.join(self.dir, status)
        os.rename(self.status_path, status_path)

        self.status = status
        self.status_path = status_path


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--log",
    "-l",
    default=False,
    is_flag=True,
    help="will log stdout and stderr to a file log.txt instead of stdout, useful when using "
    "screen for example",
)
@click.option("--tag", "-t", default="", help="only run configs with the tag")
@click.argument("config")
def run(config, log, tag):
    run_(config, log, tag)


def run_(config, log, tag, skip_done=False):
    if isinstance(config, str):
        config = yaml.load(open(config, "r"), Loader=yaml.FullLoader)

    if isinstance(config, list):
        for config_ in config:
            sys.stdout = sys.__stdout__
            run_(config_, log, tag, skip_done=True)

    else:
        status = Status(config["job_dir"])
        if tag:
            if not tag in config.get("tag", ''):
                return

        if status.status == "Running" or status.status == "Done":
            if skip_done:
                print(
                    f"Skipping {config['job_id']} because status is {status.status} ... "
                )
                return
            if not permission_to_continue(f"Job is {status.status}."):
                print("job aborted")
                return

        run_job(config, log)


def run_job(config, log):
    job_dir = config["job_dir"]
    status = Status(job_dir)

    print_running_job(config)

    if log:
        sys.stdout = open(os.path.join(job_dir, "stdout.log"), "w")
        sys.stderr = open(os.path.join(job_dir, "stderr.log"), "w")

    utils.save_git_sha(job_dir)

    status.running()

    try:
        module = _import_module(config["script_path"])
        if not hasattr(module, "main"):
            raise RuntimeError(f"{config['script_path']} has no main function.")

        module.main(config)
        status.done()

    except Exception:  # pylint: disable=broad-except
        status.failed()
        print(traceback.format_exc())


def print_running_job(config):
    msg = f"Running job {config['job_id']}"
    hashs = (8 + len(msg)) * "#"

    print(f"\n{hashs}\n{'    '+msg}\n{hashs}\n")
    print("Configuration:\n")

    pprint.pprint(config)
    print(f"\n{hashs}\n")


def permission_to_continue(msg):
    return input(msg + "Type 'y' or 'yes' to continue anyways\n").lower() in [
        "y",
        "yes",
    ]


def _import_module(path):
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _uncomitted():
    if not utils.GIT_CONTROL:
        return False

    cmd = r"git status | grep -q '\smodified:\s'"
    code = os.system(cmd)
    return code == 0
