#!/usr/bin/env python3

import json
import random
import os
import signal
import sys
import time
import argparse

from dwq import Job, Disque
import dwq.util as util

from dwq.version import __version__


def sigterm_handler(signal, stack_frame):
    raise SystemExit()


def nicetime(time):
    secs = round(time)
    minutes = secs / 60
    hrs = minutes / 60
    days = int(hrs / 24)
    secs = int(secs % 60)
    minutes = int(minutes % 60)
    hrs = int(hrs % 24)
    res = ""
    if days:
        res += "%id:" % days
    if hrs:
        res += "%ih:" % hrs
    if minutes:
        if hrs and minutes < 10:
            res += "0"
        res += "%im:" % minutes
    if minutes and secs < 10:
        res += "0"
    res += "%is" % secs
    return res


def parse_args():
    parser = argparse.ArgumentParser(
        prog="dwqc", description="dwq: disque-based work queue"
    )

    parser.add_argument(
        "-q",
        "--queue",
        type=str,
        help='queue name for jobs (default: "default")',
        default=os.environ.get("DWQ_QUEUE") or "default",
    )

    parser.add_argument(
        "-r",
        "--repo",
        help="git repository to work on",
        type=str,
        required="DWQ_REPO" not in os.environ,
        default=os.environ.get("DWQ_REPO"),
    )

    parser.add_argument(
        "-c",
        "--commit",
        help="git commit to work on",
        type=str,
        required="DWQ_COMMIT" not in os.environ,
        default=os.environ.get("DWQ_COMMIT"),
    )

    parser.add_argument(
        "-e",
        "--exclusive-jobdir",
        help="don't share jobdirs between jobs",
        action="store_true",
    )

    parser.add_argument(
        "-E",
        "--env",
        help="export environment variable to client",
        type=str,
        action="append",
        default=[],
    )
    parser.add_argument(
        "-F",
        "--file",
        help="send file along with job",
        type=str,
        action="append",
        default=[],
    )
    parser.add_argument(
        "-a",
        "--asset",
        help="save specific asset",
        type=str,
        action="append",
        default=[],
    )
    parser.add_argument(
        "-A", "--asset-dir", help="save all assets", type=str, action="store"
    )
    parser.add_argument(
        "-v", "--verbose", help="enable status output", action="store_true"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    parser.add_argument("command", type=str, nargs="+")

    return parser.parse_args()


def get_env(env):
    result = {}
    for var in env:
        var = var.split("=", maxsplit=1)
        if len(var) == 1:
            val = os.environ.get(var[0])
            if val:
                var.append(val)
            else:
                continue
        result[var[0]] = var[1]

    return result


def create_body(args, command, options=None, parent_id=None):
    body = {"repo": args.repo, "commit": args.commit, "command": command}
    if options:
        body["options"] = options

    if parent_id:
        body["parent"] = parent_id

    env = {}
    if args.env:
        env.update(get_env(args.env))

    env.update(options.get("env", {}))
    if env:
        body["env"] = env

    return body


def vprint(*args, **kwargs):
    global verbose
    if verbose:
        print(*args, **kwargs)


verbose = False


def dict_addset(_dict, key, data):
    try:
        _dict[key].add(data)
    except KeyError:
        _dict[key] = {data}


def dict_dictadd(_dict, key):
    try:
        return _dict[key]
    except KeyError:
        _tmp = {}
        _dict[key] = _tmp
        return _tmp


def handle_assets(job, args):
    assets = job["result"].get("assets")
    asset_dir = args.asset_dir

    if assets:
        asset_map = {}
        for _asset in args.asset:
            _split = _asset.split(":")
            if len(_split) == 1:
                remote = _asset
                local = _asset
            elif len(_split) == 2:
                remote, local = _split
            else:
                print('dwqc: error: invalid asset spec "%s"' % _asset, file=sys.stderr)
                sys.exit(1)

            asset_map[remote] = local

        for remote, data in assets.items():
            local = asset_map.get(remote)
            if not local:
                if asset_dir:
                    local = os.path.realpath(os.path.join(asset_dir, remote))
                    if not local.startswith(asset_dir):
                        print(
                            'dwqc: warning: asset "%s" is not relative'
                            ' to "%s", ignoring' % (remote, asset_dir),
                            file=sys.stderr,
                        )
                else:
                    print(
                        'dwqc: warning: ignoring asset "%s"' % remote, file=sys.stderr
                    )
                    continue
            util.write_files({local: data})


def main():
    global verbose
    args = parse_args()
    verbose = args.verbose

    signal.signal(signal.SIGTERM, sigterm_handler)

    job_queue = args.queue

    Disque.connect(["localhost:7711"])
    vprint("connected")

    control_queue = "control::%s" % random.random()

    try:
        file_data = util.gen_file_data(args.file)
    except util.GenFileDataException as e:
        print("dwqc: error processing --file argument:", e, file=sys.stderr)
        sys.exit(1)

    result_list = []
    exit_status = 1
    try:
        options = {"max_retries": 0, "live_output": True}
        if args.exclusive_jobdir:
            options.update({"jobdir": "exclusive"})
        if file_data:
            options["files"] = file_data

        job_id = Job.add(
            job_queue,
            create_body(args, args.command, options, None),
            [control_queue],
            retry=0,
        )
        vprint("dwqr: job with id", job_id)

        done = False
        while not done:
            vprint("dwqr: waiting for messages")
            for job in Job.wait(control_queue, count=128):
                print(job)
                if job.get("state", "") == "done":
                    print(job["result"]["output"], end="")
                    exit_status = job["result"]["status"]
                    done = True
                    break

    except (KeyboardInterrupt, SystemExit):
        print("dwqc: cancelling...")
        sys.exit(1)
    sys.exit(exit_status)
