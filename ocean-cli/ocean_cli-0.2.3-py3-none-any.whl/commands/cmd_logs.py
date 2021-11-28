import click
import multiprocessing
import time
import urllib3
import json
import sys

from ocean import api, code, utils
from ocean.main import pass_env
from ocean.utils import sprint, PrintType


@click.command()
@click.argument("job-name")
@click.option("-id", default=0, help="Task ID of job.")
@pass_env
def cli(ctx, job_name, id):
    _logs_v2(ctx, job_name, id)


def _logs_v2(ctx, job_name, id):

    job_uid, pod_uid = None, None
    is_pending = True

    while is_pending:
        # Job info request
        res = api.get(ctx, code.API_JOB)
        body = utils.dict_to_namespace(res.json())

        # get job uid, pod uid
        for job in body.jobsInfos:
            if job.name == job_name:
                for task in job.jobs:
                    if task.name == job.name + "-" + str(id):
                        if len(task.jobPodInfos) <= 0:
                            sprint("Log not found.", PrintType.FAILED)
                            return
                        sprint(
                            "\033[2Kstatus: " + task.jobPodInfos[0].status + "\r",
                            PrintType.WORNING,
                            nl=False,
                        )
                        # print("\033[2K\033[1G", nl=False)
                        if task.jobPodInfos[0].status not in [
                            "Pending",
                            "ContainerCreating",
                        ]:
                            job_uid = task.uid
                            pod_uid = task.jobPodInfos[0].uid
                            is_pending = False
                            sprint("")
                        break
                else:
                    raise ValueError()
                break
        else:
            raise ValueError()

    # Log stream
    print(job_uid, pod_uid)
    log = multiprocessing.Process(target=print_logs, args=(ctx, job_uid, pod_uid))

    try:
        log.start()
        log.join()
    except KeyboardInterrupt:
        log.terminate()
    except Exception:
        log.terminate()


def print_logs(ctx, job_uid, pod_uid):
    try:
        with api.get(
            ctx,
            f"{code.API_LOG}?jobUid={job_uid}&podUid={pod_uid}",
            timeout=None,
            stream=True,
        ) as r:
            for line in r.iter_lines():
                print(line.decode(), flush=True)
    except KeyboardInterrupt:
        return
