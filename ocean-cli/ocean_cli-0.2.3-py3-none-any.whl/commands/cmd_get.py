import click
from datetime import datetime, timezone

from ocean import api, code, utils
from ocean.main import pass_env
from ocean.utils import sprint, PrintType


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


# Workloads
@cli.command()
@pass_env
def instances(ctx):
    res = api.get(ctx, "/api/instances/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:20} {:10} {:15} {:15}"

    sprint(fstring.format("NAME", "STATUS", "TYPE", "VOLUME"))
    for pods in body.pods:
        sprint(
            fstring.format(
                pods.name,
                pods.status,
                pods.labels.machineType.name,
                pods.volumes[0].persistentVolumeClaim.claimName,
            )
        )


@cli.command()
@click.option("-d", "--detail", help="Show selected sub tasks detail")
@click.option(
    "-A",
    "--detail-all",
    is_flag=True,
    help="Show all sub tasks detail. `--detail` option will be ignored.",
)
@pass_env
def jobs(ctx, detail=None, detail_all=None):
    detail = detail.split(",") if detail else None

    # conditions
    print_detail = detail or detail_all
    print_simple = (detail is None) and (not detail_all)
    filter_job = lambda x: print_simple or detail_all or (x in detail)

    # api call
    res = api.get(ctx, "/api/jobs/")
    body = utils.dict_to_namespace(res.json())

    fstring = "{:20} {:4} {:4} {:4} {:4} {:7} {:15} {:15} {:50} {:20}"

    sprint(
        fstring.format(
            "NAME",
            "WAIT",
            "RUN",
            "SUCC",
            "FAIL",
            "UNKNOWN",
            "TYPE",
            "VOLUME",
            "IMAGE",
            "COMMAND",
        )
    )
    for jobInfo in body.jobsInfos:
        if not filter_job(jobInfo.name):
            continue

        pending, running, succeeded, failed, unknown = 0, 0, 0, 0, 0
        details = []
        for job in jobInfo.jobs:
            if len(job.jobPodInfos) > 0:
                status = job.jobPodInfos[0].status
                if status == "Pending":
                    pending += 1
                elif status == "Running":
                    running += 1
                elif status == "Succeeded":
                    succeeded += 1
                elif status == "Failed":
                    failed += 1
            else:
                unknown += 1

            if print_detail:
                start_time = utils.convert_time(job.startTime)
                complete_time = utils.convert_time(job.completionTime)
                delta = 0
                if status == "Running":
                    delta = (
                        datetime.now(timezone.utc).replace(microsecond=0) - start_time
                    )
                elif status == "Succeeded":
                    delta = complete_time - start_time

                start_time = utils.date_format(start_time)
                complete_time = utils.date_format(complete_time)

                details.append(
                    f"{job.name:20} {job.jobPodInfos[0].status:10} {start_time} ~ {complete_time} ({delta})"
                )

        sprint(
            fstring.format(
                jobInfo.name,
                str(pending),
                str(running),
                str(succeeded),
                str(failed),
                str(unknown),
                jobInfo.labels.machineType.name,
                jobInfo.volumes[0].persistentVolumeClaim.claimName,
                jobInfo.image,
                jobInfo.command,
            )
        )
        if print_detail:
            sprint("\n".join(details))
            sprint()


@cli.command()
@pass_env
def volumes(ctx):
    content = _volumes(ctx)

    sprint(content.fstring.format(*content.header))
    for item in content.items:
        sprint(content.fstring.format(*item))


def _volumes(ctx):
    res = api.get(ctx, "/api/volumes/")
    body = utils.dict_to_namespace(res.json())

    content = utils.dict_to_namespace(
        {
            "fstring": "{:20} {:10} {:10}",
            "header": ["NAME", "STATUS", "CAPACITY"],
            "items": [],
        }
    )

    for vol in body.volumes:
        content.items.append([vol.name, vol.status, vol.capacity])

    return content


# Resources
@cli.command()
@pass_env
def images(ctx):
    content = _images(ctx)

    sprint(content.fstring.format(*content.header))
    for item in content.items:
        sprint(content.fstring.format(*item))


def _images(ctx):
    content = utils.dict_to_namespace(
        {
            "fstring": "{:11} {:10} {:80} {}",
            "header": ["TYPE", "STATUS", "IMAGE", "LABLES"],
            "items": [],
        }
    )

    # public, user images
    res = api.get(ctx, "/api/images/")
    body = utils.dict_to_namespace(res.json())

    images_list = body.public + body.user

    # snapshot
    res = api.get(ctx, "/api/instances")

    for uid in map(lambda x: x["podUid"], res.json()["pods"]):
        res = api.get(ctx, f"/api/images/commit/{uid}")
        body = res.json()

        images_list += utils.dict_to_namespace(body["workHistory"][uid]["images"])

    # insert
    for img in images_list:
        content.items.append(
            [img.imageType, img.imageStatus, img.imageName, ",".join(img.imageLabels)]
        )

    return content


@cli.command()
@pass_env
def quota(ctx):
    content = _quota(ctx)

    for item in content.items:
        sprint(content.fstring.format(*item))


def _quota(ctx):
    res = api.get(ctx, "/api/users/resources")

    body = utils.dict_to_namespace(res.json())

    content = utils.dict_to_namespace(
        {
            "fstring": "{:20} {:10} {:100}",
            "header": ["MACHINETYPE", "QUOTA", "SPEC"],
            "items": [],
        }
    )

    for mt in body.machineTypes:
        content.items.append(
            [
                mt.name,
                f"{mt.quotaUsedIn}/{mt.quota}",
                f"CPU {mt.cpus:2}, MEM {mt.memory:3} Gi, GPU {mt.gpus:1} x {mt.gpuType}",
            ]
        )

    return content


@cli.command()
@pass_env
def requests(ctx):
    content = _requests(ctx)

    sprint(content.fstring.format(*content.header))
    for item in content.items:
        sprint(content.fstring.format(*item))


def _requests(ctx):
    res = api.get(ctx, "/api/resources/request")

    body = utils.dict_to_namespace(res.json())

    content = utils.dict_to_namespace(
        {
            "fstring": "{:10} {:20} {:10} {:12} {:12} {:50}",
            "header": [
                "STATUS",
                "MACHINETYPE",
                "QUOTA",
                "START",
                "END",
                "REJECTED REASON",
            ],
            "items": [],
        }
    )

    for req in body:
        content.items.append(
            [
                req.status,
                req.machineType.name,
                str(req.quota),
                req.startDate[:10],
                req.endDate[:10],
                f"{req.rejectedReason}",
                req.id,
            ]
        )

    return content


@cli.command()
@pass_env
def machine_types(ctx):
    content = _machine_types(ctx)

    sprint(content.fstring.format(*content.header))
    for item in content.items:
        sprint(content.fstring.format(*item))


def _machine_types(ctx):
    res = api.get(ctx, "/api/machinetypes/")

    body = utils.dict_to_namespace(res.json())

    content = utils.dict_to_namespace(
        {"fstring": "{:20} {:100}", "header": ["NAME", "SPEC"], "items": []}
    )

    for mt in body:
        content.items.append(
            [
                mt.name,
                f"CPU {mt.cpus:4}, MEM {mt.memory:5} Gi, GPU {mt.gpus:1} x {mt.gpuType}",
                mt.id,
            ]
        )
    return content


# CLI ENV
@cli.command()
@pass_env
def presets(ctx):
    _presets(ctx)


def _presets(ctx, show_id=False):
    fstring = "{:20} {:15} {:10} {:40}"
    fstring = "{id:5} " + fstring if show_id else fstring

    sprint(fstring.format("NAME", "TYPE", "VOLUME", "IMAGE", id="ID"))
    for preset in utils.dict_to_namespace(ctx.get_presets()):
        default_txt = " (default)" if preset.default else ""
        sprint(
            fstring.format(
                preset.name + default_txt,
                preset.machineType,
                preset.volume,
                f"{preset.image} ({preset.imageType})",
            )
        )
