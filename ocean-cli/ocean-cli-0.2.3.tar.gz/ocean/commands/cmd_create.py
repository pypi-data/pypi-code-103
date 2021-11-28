import click
from datetime import datetime
from dateutil.relativedelta import relativedelta
import inquirer
import uuid

# from simple_term_menu import TerminalMenu

from ocean import api, code, utils
from ocean.main import pass_env
from ocean.commands import cmd_get, cmd_logs, cmd_delete
from ocean.utils import sprint, PrintType


@click.group(cls=utils.AliasedGroup)
def cli():
    pass


@cli.command()
@click.option("--name", "-n", required=True, help="image name from docker hub.")
@click.option("--label", "-l", help="label of image. one of ['vscode'].")
@pass_env
def image(ctx, name, label):
    if label not in ["vscode", None]:
        sprint(f"not allowed labels: {label}. Only allows 'vscode'.", PrintType.FAILED)
        return
    data = {"imageName": name, "imageType": "user", "imageLabel": ""}
    api.post(ctx, code.API_IMAGE, data=data)
    sprint("Image pull request done.", PrintType.SUCCESS)
    sprint("\n\tcheck status with `ocean get images`.")


# Workloads
@cli.command()
@click.option("--name", "-n", help="job name.")
@click.option("-p", "--preset", help="run job with preset configuration")
@click.option("--purpose", default="None", help="purpose of job")
@click.option(
    "-i", "--image", help="base docker image. `image type` must be specified."
)
@click.option(
    "-t", "--image-type", help="base docker image type. `image` must be specified."
)
@click.option("-m", "--machine-type", help="machine-type to run this job")
@click.option("-v", "--volume", help="mounted volume")
@click.option("-r", "--repeat", default=1, help="how many repeat same job")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="debug mode. follows logs and delete when finished.",
)
@click.argument("command", nargs=-1, type=click.Path())
@pass_env
def job(
    ctx,
    name,
    preset,
    purpose,
    image,
    image_type,
    machine_type,
    volume,
    repeat,
    debug,
    command,
):
    if not name:
        name = uuid.uuid4().hex[:6]

    # image and image type both nessery and sufficiend condition.
    if bool(image) != bool(image_type):
        sprint("`image` and `image type` both are need.", PrintType.FAILED)
        return
    if image_type not in ["public", "user", None]:
        sprint("`image type` must be 'public' or 'user'.", PrintType.FAILED)
        return

    preset_condition = lambda p: (preset == p.name) if preset else p.default
    presets = utils.dict_to_namespace(ctx.get_presets())
    for p in presets:
        if preset_condition(p):
            image = image if image else p.image
            image_type = image_type if image_type else p.imageType
            machine_type = machine_type if machine_type else p.machineType
            volume = volume if volume else p.volume
            break
    else:
        sprint("Invalid `preset`.", PrintType.FAILED)
        sprint("Please check allowed preset here:\n\n\tocean get preset\n")
        exit()

    if purpose == "" or purpose is None:
        sprint("`purpose` cannot be blank.", PrintType.FAILED)
        exit()

    mid = api.get_id_from_machine_type(ctx, machine_type)
    if mid is None:
        sprint("Invalid `machine-type`.", PrintType.FAILED)
        sprint("Please check allowed machine-type here:\n\n\tocean get quota\n")
        exit()

    vid = api.get_volume_id_from_volume_name(ctx, volume)

    data = {
        code.NAME: name,
        code.PURPOSE: purpose,
        code.IMAGE: image,
        code.IMAGE_TYPE: image_type,
        code.MACHINETYPEID: mid,
        code.VOLUMENAME: vid,
        code.REPEAT: repeat,
        code.COMMAND: " ".join(command),
    }

    res = api.post(ctx, code.API_JOB, data=data)
    sprint(f"Job `{name}` Created.", PrintType.SUCCESS)

    if debug:
        # show logs
        cmd_logs._logs_v2(ctx, name, 0)

        # delete job
        cmd_delete._jobs(ctx, name)


@cli.command()
@pass_env
def presets(ctx):
    try:
        # Data
        machine_types = cmd_get._quota(ctx)
        if len(machine_types.items) <= 0:
            sprint(
                "No possible Machine Types. Please request quota first.",
                PrintType.FAILED,
            )
            return
        images = cmd_get._images(ctx)
        if len(images.items) <= 0:
            sprint(
                "No possible Images. Please upload new Image or request to admin.",
                PrintType.FAILED,
            )
            return
        volumes = cmd_get._volumes(ctx)
        if len(images.items) <= 0:
            sprint(
                "No possible Volume. Please create new Volume.",
                PrintType.FAILED,
            )
            return

        # Prompt
        name = click.prompt("Preset Name")
        # name = inquirer.text(message="Preset Name")       ## windows10에서 backspace 문자열 문제

        presets = ctx.get_presets()
        while name in map(lambda x: x["name"], presets):
            sprint(f"Preset `{name}` already exit.\n", PrintType.FAILED)
            name = click.prompt("Preset Name")
            # name = inquirer.text(message="Preset Name")   ## windows10에서 backspace 문자열 문제

        display_machine_types = [
            machine_types.fstring.format(*x) for x in machine_types.items
        ]
        machine_type = inquirer.list_input(
            "MachineType",
            choices=display_machine_types,
        )
        machine_type = machine_types.items[display_machine_types.index(machine_type)][0]

        disply_images = [images.fstring.format(*x) for x in images.items]
        image = inquirer.list_input(
            "Image",
            choices=disply_images,
        )
        imageType, _, image, _ = images.items[disply_images.index(image)]

        disply_volumes = [volumes.fstring.format(*x) for x in volumes.items]
        volume = inquirer.list_input(
            "Volume",
            choices=disply_volumes,
        )
        volume = volumes.items[disply_volumes.index(volume)][0]

        default = click.confirm("Set to default?")  ## windows10에서 backspace 문자열 문제
    except TypeError as e:
        sprint("Abort!", PrintType.FAILED)
        return

    preset = {
        code.NAME: name,
        code.MACHINETYPE: machine_type,
        code.IMAGE: image,
        code.IMAGE_TYPE: imageType,
        code.VOLUME: volume,
        code.DEFAULT: default,
    }
    ctx.add_presets(preset)
    sprint(f"Preset `{name}` Created.", PrintType.SUCCESS)


@cli.command()
@pass_env
def request(ctx):
    machine_types = cmd_get._machine_types(ctx)
    if len(machine_types.items) <= 0:
        sprint("No available Machine Types. Please request to admin.", PrintType.FAILED)
        return

    machine_types_choices = [
        machine_types.fstring.format(*x) for x in machine_types.items
    ]
    period_choices = [
        "1 days",
        "1 weeks",
        "2 weeks",
        "1 months",
        "2 months",
        "6 months",
    ]

    q = [
        inquirer.List(
            code.MACHINETYPE, message="Machine Type", choices=machine_types_choices
        ),
        inquirer.Text(
            code.QUOTA, message="How many requests?", validate=quota_validation
        ),
        inquirer.List(
            code.PERIOD,
            message="Period of use",
            choices=period_choices,
            default="1 weeks",
        ),
        inquirer.Text(code.REASON, message="Reason", validate=reason_validation),
        # inquirer.Confirm(code.CONFIRM, message="Correct?")
    ]

    answers = inquirer.prompt(q)

    idx = machine_types_choices.index(answers[code.MACHINETYPE])
    start_date = datetime.today()
    end_date = start_date + parse_delta(answers[code.PERIOD])

    data = {
        code.MACHINETYPEID: machine_types.items[idx][2],
        code.QUOTA: answers[code.QUOTA],
        code.STARTDATE: start_date.isoformat(),
        code.ENDDATE: end_date.isoformat(),
        code.REASON: answers[code.REASON],
    }
    res = api.post(ctx, code.API_REQUEST, data=data)
    sprint(f"Request Quota Submitted.", PrintType.SUCCESS)
    return


def quota_validation(answers, current):
    try:
        current = int(current)
        return current > 0
    except ValueError:
        return False


def reason_validation(answers, current):
    return current != ""


def parse_delta(string):
    num, unit = string.split(" ")
    num = int(num)
    if unit == "days":
        return relativedelta(days=num)
    elif unit == "weeks":
        return relativedelta(weeks=num)
    elif unit == "months":
        return relativedelta(months=num)
    else:
        raise ValueError(f"Unable to parse: {string}")


def get_idx(message, length):
    id = click.prompt(message, type=int)
    in_range = id in range(length)
    while not in_range:
        sprint(f"Error: '{id}' is not a valid integer.", PrintType.FAILED)
        id = click.prompt(message, type=int)
        in_range = id in range(length)
    return id
