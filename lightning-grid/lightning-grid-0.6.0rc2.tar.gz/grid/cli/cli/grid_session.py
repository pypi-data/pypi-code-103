import subprocess
from typing import Optional
import warnings

import click

from grid import Datastore, list_datastores, Session
from grid.cli import rich_click
from grid.cli.cli.grid_run import _check_run_name_is_valid, _get_instance_types, _resolve_instance_type_nickname
from grid.cli.cli.utilities import validate_disk_size_callback, read_config_callback
from grid.cli.client import Grid
from grid.cli.types import ObservableType
from grid.sdk.utils.name_generator import unique_name
from grid.sdk import env

WARNING_STR = click.style('WARNING', fg='yellow')
SUCCESS_MARK = click.style("✔", fg='green')
FAIL_MARK = click.style('✘', fg='red')


@rich_click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
def session(ctx, is_global: bool) -> None:
    """
    Contains a grouping of commands to manage sessions workflows.

    Executing the `grid session` command without any further arguments
    or comands renders a list of all sessions registered to your Grid
    user account.
    """
    client = Grid()
    if ctx.invoked_subcommand is None:
        # Get the status of the interactive observables.
        kind = ObservableType.INTERACTIVE
        client.status(kind=kind, follow=False, is_global=is_global)
    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@session.command()
@rich_click.argument(
    'name', type=str, required=False, default=None, help='Name for this run', callback=_check_run_name_is_valid
)
@click.option('--cluster', 'cluster', type=str, required=False, default=None, help='Cluster to run on')
@click.option(
    '--instance_type',
    'instance_type',
    type=str,
    default='t2.medium',
    callback=_resolve_instance_type_nickname,
    help='Instance type to start session in.',
    autocompletion=_get_instance_types
)
@click.option(
    '--use_spot',
    'use_spot',
    is_flag=True,
    required=False,
    default=False,
    help='Use spot instance. The spot instances, or preemptive instance can be shut down at will'
)
@click.option(
    '--disk_size',
    'disk_size',
    type=int,
    required=False,
    default=200,
    callback=validate_disk_size_callback,
    help='The disk size in GB to allocate to the session.'
)
@click.option(
    '--datastore_name',
    'datastore_name',
    type=str,
    required=False,
    default=None,
    help='Datastore name to be mounted in the session.'
)
@click.option(
    '--datastore_version',
    'datastore_version',
    type=str,
    required=False,
    default=None,
    help='Datastore version to be mounted in the session.'
)
@click.option(
    '--datastore_mount_dir',
    'datastore_mount_dir',
    type=str,
    required=False,
    default=None,
    help='Absolute path to mount Datastore in the session (defaults to /datastores/<datastore-name>).'
)
@click.option(
    '--config',
    'config',
    type=click.File('r'),
    required=False,
    default=None,
    callback=read_config_callback,
    help='Path to Grid config YML'
)
def create(
    name: Optional[str],
    cluster: Optional[str],
    instance_type: str,
    datastore_name: Optional[str],
    datastore_version: Optional[str],
    datastore_mount_dir: Optional[str],
    disk_size: int,
    use_spot: bool,
    config: Optional[dict],
) -> None:
    """Creates a new interactive session with NAME.

    Interactive sessions are optimized for development activites (before executing
    hyperparemeter sweeps in a Run). Once created, sessions can be accessed via
    VSCode, Jupyter-lab, or SSH interfaces.

    Grid manages the installation of any/all core libraries, drivers, and interfaces
    to the outside world. Sessions can be run on anything from a small 2 CPU core +
    4GB memory instance to a monster machine with 96 CPU cores + 824 GB memory + eight
    V100 GPUs + 40 GBPS netowrk bandwidth (no, those values aren't typos!); or really
    anything in between.
    """
    client = Grid()
    client.check_is_blocked()

    # The config option should be deprecated. This just takes the file passed in an
    # attempts to get the values provided within it, defaulting back to the standard
    # CLI click option values if they are not provided.
    if config is not None:
        _default_cluster = cluster if cluster is not None else env.CONTEXT
        cluster = config.get('compute', {}).get('provider', {}).get('cluster', _default_cluster)
        instance_type = config.get('compute', {}).get('train').get('instance_type', instance_type)
        disk_size = config.get('compute', {}).get('train', {}).get('disk_size', disk_size)
        datastore_name = config.get('compute', {}).get('train', {}).get('datastore_name', datastore_name)
        datastore_version = config.get('compute', {}).get('train', {}).get('datastore_version', datastore_version)
        datastore_mount_dir = config.get('compute', {}).get('train', {}).get('datastore_mount_dir', datastore_mount_dir)
        use_spot = config.get('compute', {}).get('train', {}).get('use_spot', use_spot)

    # make a fun random name when user does not pass in a name
    if name is None:
        name = unique_name()

    # process datastore specification args
    dstore_kwargs = {}
    if datastore_name is not None:
        owner = None
        if ':' in datastore_name:
            owner, datastore_name = datastore_name.split(':')

        if datastore_version is None:  # select the max version available
            possible_dstore_versions = [d for d in list_datastores(include_teams=True) if d.name == datastore_name]
            datastore_version = max([d.version for d in possible_dstore_versions])
            warnings.warn(
                f'No ``--datastore_version`` passed. Using datastore: {datastore_name} version: {datastore_version}'
            )

        try:
            dstore = Datastore(name=datastore_name, version=datastore_version, owner=owner, cluster_id=cluster)
        except Exception as e:
            raise click.ClickException(
                f'No ready-to-use datastore found with name {datastore_name} '
                f'and version {datastore_version}. Internal Error: {e}'
            )
        dstore_kwargs['datastores'] = {datastore_mount_dir: dstore}

    sess = Session(
        name=name,
        instance_type=instance_type,
        disk_size_gb=disk_size,
        use_spot=use_spot,
        cluster_id=cluster,
        **dstore_kwargs,
    )
    if sess.currently_exists is True:
        raise click.ClickException(f"A session with the name: {name} already exists. Please specify a unique name.")

    click.echo("Creating Interactive session ...", color="yellow")
    try:
        sess.start()
        click.echo(
            f"""
        {SUCCESS_MARK} Interactive session created!

        `grid status` to list all runs and interactive sessions.
        `grid status {name}` to see the status for this interactive session.

        ----------------------
        Submission summary
        ----------------------
        name:                    {name}
        instance_type:           {sess.instance_type}
        cluster_id:              {sess.cluster_id}
        datastore_name:          {datastore_name}
        datastore_version:       {datastore_version}
        datastore_mount_dir:     {datastore_mount_dir}
        use_spot:                {sess.use_spot}
        """
        )
        click.echo(f"Interactive session {name} is spinning up.")
    except Exception as e:
        # TODO: credit card validation for GPU instances.
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(str(e))


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def pause(session_name: str) -> None:
    """Pauses a session identified by the SESSION_NAME.

    Pausing a session stops the running instance (and any computations being
    performed on it - be sure to save your work!) and and billing of your account
    for the machine. The session can be resumed at a later point with all your
    persisted files and saved work unchanged.
    """
    click.echo("Pausing Interactive session ...", color="yellow")

    try:
        Session(name=session_name).pause()
        click.echo(SUCCESS_MARK)
        click.echo(f'Interactive session {session_name} has been paused successfully.')
    except Exception as e:
        click.echo("✘", color="red")
        raise click.ClickException(f"Failed to pause interactive session: '{session_name}'")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def resume(session_name: str) -> None:
    """Resumes a session identified by SESSION_NAME.
    """
    click.echo("Resuming Interactive session ...", color="yellow")

    try:
        Session(name=session_name).start()
        click.echo(f'{SUCCESS_MARK} Interactive session: {session_name} successfully began resuming.')
        click.echo('Note: Depending on instance-type selected, it may take up to 10 minutes to become available.')
    except Exception as e:
        click.echo(f"{FAIL_MARK} {e}")
        raise click.ClickException(f"Failed to resume interactive session: '{session_name}'")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1)
def delete(session_name: str) -> None:
    """Deletes a session identified by SESSION_NAME.

    Deleting a session will stop the running instance (and any computations being
    performed on it) and billing of your account. All work done on the machine
    is permenantly removed, including all/any saved files, code, or downloaded
    data (assuming the source of the data was not a grid datastore - datastore
    data is not deleted).
    """
    click.echo("Deleting Interactive node ...", color="yellow")

    try:
        Session(name=session_name).delete()
        click.echo(f'{SUCCESS_MARK} Interactive node {session_name} has been deleted successfully.')
    except Exception as e:
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(f"Failed to delete interactive session '{session_name}'")


@session.command()
@rich_click.argument('session_name', type=str, nargs=1, help='Name of the session to change')
@rich_click.argument('instance_type', type=str, nargs=1, help='Instance type to change to')
@click.option(
    '--spot',
    type=bool,
    is_flag=True,
    default=None,
    show_default=True,
    help='Use a spot instance to launch the session'
)
@click.option(
    '--on_demand',
    '--on-demand',
    'on_demand',
    type=bool,
    is_flag=True,
    default=None,
    show_default=True,
    help='Use an on-demand instance to launch the session'
)
def change_instance_type(
    session_name: str, instance_type: str, spot: Optional[bool], on_demand: Optional[bool]
) -> None:
    """
    Change the instance type of a session; this allows you to upgrade
    or downgrade the compute capability of the session nodes while keeping
    all of your work in progress untouched.

    The session must be PAUSED in order for this command to succeed

    Specifying --spot allows you to change the instance to an interuptable
    spot instances (which come at a steap discount, but which can be
    interrupted and shut down at any point in time depending on cloud
    provider instance type demand).

    specifying --on_demand changes the instance to an on-demand type,
    which cannot be inturrupted but is more expensive.
    """
    click.echo("Changing Session Instance Type ...", color="yellow")

    if (spot is True) and (on_demand is True):
        raise click.ClickException('cannot pass both --spot and --on_demand flags to this command.')

    use_spot = True if spot else False if on_demand else None

    try:

        Session(name=session_name).change_instance_type(instance_type=instance_type, use_spot=use_spot)
        click.echo(f'{SUCCESS_MARK} Interactive session {session_name} instance type changed successfully.')
    except Exception as e:
        click.echo(f'{FAIL_MARK} {e}')
        raise click.ClickException(f"Failed to change session instance type '{session_name}'")


def _update_ssh_config_and_check_ixsession_status(ctx, param, value: str) -> int:
    """
    This updates the SSH config for interactive nodes and
    also checks if those nodes can be interacted with SSH
    before attempting an operation. This prevents SSHing into
    nodes that are not un a running state, e.g. paused or pending.

    This manages a section within user's ssh config file
    for all interactive nodes shh config details

    Afterwards you can use systems ssh & related utilities
    (sshfs, rsync, ansible, whatever) with interactive nodes
    directly

    The default file is ~/.ssh/config and  can be changed via
    envvar GRID_SSH_CONFIG

    Returns
    --------
    value: str
        Unmodified value if valid
    """
    client = Grid()
    nodes = client.sync_ssh_config()

    click.echo(f"Sync config for {len(nodes)} interactive nodes")

    target_ixsession = None
    for node in nodes:
        if node["name"] == value:
            target_ixsession = node

    # Check if interactive session exists at all
    if not target_ixsession:
        session_names = [n["name"] for n in nodes]
        raise click.BadArgumentUsage(
            f"Interactive session {value} does not exist. "
            f"Available Interactive Sessions are: {', '.join(session_names)}"
        )

    # Check if the node is in 'running' status
    if target_ixsession["status"] != "running":
        running_ixsessions = [n["name"] for n in nodes if n["status"] == "running"]
        raise click.BadArgumentUsage(
            f"Interactive session {value} is not ready. "
            f"Sessions that are ready to SSH are: {', '.join(running_ixsessions)}"
        )

    return value


@session.command()
@rich_click.argument(
    'node_name',
    type=str,
    callback=_update_ssh_config_and_check_ixsession_status,
    help="The name of the node. This command executes ssh <node name>.",
)
@rich_click.argument('ssh_args', nargs=-1, type=click.UNPROCESSED, help="Arguments to be forwarded to the SSH command.")
def ssh(node_name, ssh_args):
    """SSH into the interactive node identified by NODE_NAME.

    If you'd like the full power of ssh, you can use any ssh client and
    do `ssh <node_name>`. This command is stripped down version of it.

    Example:

        1. Path to custom key:

        grid session ssh satisfied-rabbit-962 -- -i ~/.ssh/my-key

        2. Custom ssh option:

        grid session ssh satisfied-rabbit-962 -- -o "StrictHostKeyChecking accept-new"
    """
    subprocess.check_call(['ssh', node_name, *ssh_args])


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1, callback=_update_ssh_config_and_check_ixsession_status)
@rich_click.argument('mount_dir', type=str, nargs=1)
def mount(interactive_node, mount_dir):
    r"""Mount session directory to local. The session is identified by
    INTERACTIVE_NODE and MOUNT_DIR is a path to a directory on the local machine.

    To mount a filesystem use:
    ixNode:[dir] mountpoint

    Examples:
        # Mounts the home directory on the interactive node in dir data
        grid interactive mount bluberry-122 ./data

        # mounts ~/data directory on the interactive node to ./data
        grid interactive mount bluberry-122:~/data ./data

    To unmount it:
      fusermount3 -u mountpoint   # Linux
      umount mountpoint           # OS X, FreeBSD

    Under the hood this is just passing data to sshfs after syncing grid's interactive,
    i.e. this command is dumbed down sshfs

    See Also:
        grid sync-ssh-config --help
    """
    if ':' not in interactive_node:
        interactive_node += ":/home/jovyan"

    client = Grid()
    client.sync_ssh_config()

    try:
        subprocess.check_call(['sshfs', interactive_node, mount_dir])
    except FileNotFoundError:
        raise click.ClickException('Unable to mount: sshfs was not found')
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f'Unable to mount: sshfs failed with code {e.returncode}')
