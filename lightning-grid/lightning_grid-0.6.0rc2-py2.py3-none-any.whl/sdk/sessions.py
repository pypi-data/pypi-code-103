from datetime import datetime
import textwrap
from typing import Dict, List, Optional, Union
from functools import wraps

from grid.openapi import V1DatastoreInput, V1SessionSpec, V1SessionState, V1SessionStatus
from grid.sdk.client import create_swagger_client
from grid.sdk.datastore import Datastore
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.datastores import datastore_id_from_dsn, get_datastore
from grid.sdk.rest.sessions import (
    change_session_instance_type,
    create_session,
    delete_session,
    get_session,
    pause_session,
    resume_session,
    session_id_from_name,
)
from grid.sdk.user import get_teams, User, user_from_logged_in_account


def fail_if_deleted(func):
    """Decorator which raises an exception at access time if the session has been deleted.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._alive:
            raise RuntimeError('Cannot perform operation on deleted session') from None
        return func(self, *args, **kwargs)

    return wrapper


def fail_if_session_currently_exists(func):
    """Decorator which raises an exception at access time if the session has already been created.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._currently_exists:
            raise RuntimeError('Property only can be accessed before the session is created.') from None
        return func(self, *args, **kwargs)

    return wrapper


def fail_if_session_does_not_exist(func):
    """Decorator which raises an exception at access time if the session has not been created.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._currently_exists:
            raise RuntimeError('Property only can be accessed after the session is created.') from None
        return func(self, *args, **kwargs)

    return wrapper


class Session:
    """Speficy, Modify, Create, Pause, or Delete an interactive session instance.

    Interactive sessions are optimized for development activites (before executing
    hyperparemeter sweeps in a Run). Once created, sessions can be accessed via
    VSCode, Jupyter-lab, or SSH interfaces.

    Grid manages the installation of any/all core libraries, drivers, and interfaces
    to the outside world. Sessions can be run on anything from a small 2 CPU core +
    4GB memory instance to a monster machine with 96 CPU cores + 824 GB memory + eight
    V100 GPUs + 40 GBPS netowrk bandwidth (no, those values aren't typos!); or really
    anything in between.

    Parameters
    ----------
    name
        human adressable name to assign to the session instance
    instance_type
        compute node type which the session will be provisioned on
    disk_size_gb
        amount of storage provisioned to the root boot disk the session
        will be provisioned on (ie. disk storage provisioned to the user)
    datastores
        mapping of mount directories to `Datastore` instances
        which will be attached to the session instance. For example; to
        mount datastore "mnist" to the path /mydata/mnist you would pass:
        `{"/mydata/mnist": Datastore(...)}`

        If no datastore mount directory is provided as a key (ie.
        `{None: Datastore(...)}`), then the default mount directory for the
        datastore will be used. This maps to `/home/jovyan/<datastore-name>`
    use_spot
        bool indicating if a spot instance should be used when provisioining
        the underlying machine the session service operates on. If True
        then the hourly cost will be significantly reduced from the base
        (on-demand) price, but the instance can be terminated at any time.
        Upon termination your notebooks and scripts will be saved, but you may
        lose data which is "in-process".

        If False (the default), then un-interuptable on-demand instances are
        used. While this increases costs it does mean that your machine will
        not be deprovisioned if the cloud provider experiences increased
        demand for that instance type.
    cluster_id
        Bring-your-own-credential users only. specify the name of the cluster
        to operate the sesison on.
    """

    _name: str
    _id: str
    _cluster_id: str

    _datastores: Dict[str, Datastore]  # mapping ``mount path -> Datastore instance``
    _disk_size_gb: str
    _instance_type: str
    _use_spot: bool

    _hourly_cost: float
    _total_cost: float
    _total_run_time: float

    _desired_state: V1SessionState
    _last_status_state: V1SessionState

    _created_at: datetime
    _started_at: datetime
    _finished_at: datetime
    _last_state_status_transition_at: datetime

    _jupyter_lab_url: str
    _jupyter_lab_token: str
    _ssh_url: str

    _client: GridRestClient

    _user: User

    _alive: bool
    _currently_exists: bool

    def __init__(
        self,
        name: str,
        instance_type: Optional[str] = None,
        disk_size_gb: Union[int, str] = 200,
        datastores: Optional[Dict[str, Datastore]] = None,
        use_spot: bool = False,
        cluster_id: Optional[str] = None
    ):
        if datastores is None:
            datastores = {}

        self._name = name
        self._client = GridRestClient(api_client=create_swagger_client())
        try:
            self._id = session_id_from_name(self._client, self._name, cluster_id=cluster_id)
            self._currently_exists = True
            self._setup_from_existing()
            return
        except KeyError:
            self._id = None

        self._instance_type = instance_type
        self._disk_size_gb = str(disk_size_gb)

        self._datastores = {}
        for mount_dir, datastore in datastores.items():
            if mount_dir is None:
                mount_dir = f'/home/jovyan/{datastore.name}'
            self._datastores[mount_dir] = datastore

        self._use_spot = use_spot
        self._cluster_id = cluster_id

        self._user = user_from_logged_in_account()

        self._alive = True
        self._currently_exists = False

    def __repr__(self):
        self._setup_from_existing()
        if self._currently_exists is True:
            res = textwrap.dedent(
                f"""\
                {self.__class__.__name__}(
                    {"name": <17} = \"{self._name}\",
                    {"currently_exists": <17} = {self._currently_exists},
                    {"cluster_id": <17} = \"{self._cluster_id}\",
                    {"datastores": <17} = {self._datastores},
                    {"disk_size_gb": <17} = {self._disk_size_gb},
                    {"instance_type": <17} = \"{self._instance_type}\",
                    {"use_spot": <17} = {self._use_spot},
                    {"hourly_cost": <17} = {self._hourly_cost},
                    {"total_cost": <17} = {self._total_cost},
                    {"total_run_time": <17} = {self._total_run_time},
                    {"desired_state": <17} = {self._desired_state},
                    {"last_status_state": <17} = {self._last_status_state},
                    {"jupyter_lab_url": <17} = \"{self._jupyter_lab_url}\",
                    {"jupyter_lab_token": <17} = \"{self._jupyter_lab_token}\",
                    {"ssh_url": <17} = \"{self._ssh_url}\",
                )"""
            )
        else:
            res = textwrap.dedent(
                f"""\
            {self.__class__.__name__}(
                {"name": <17} = \"{self._name}\",
                {"currently_exists": <17} = {self._currently_exists},
                {"cluster_id": <17} = \"{self._cluster_id}\",
                {"datastores": <17} = {self._datastores},
                {"disk_size_gb": <17} = {self._disk_size_gb},
                {"instance_type": <17} = \"{self._instance_type}\",
                {"use_spot": <17} = {self._use_spot},
            )"""
            )
        return res

    @fail_if_deleted
    @fail_if_session_does_not_exist
    def refresh(self):
        """Update this session object the latest state from the server..
        """
        self._setup_from_existing()

    # ---------------- User Modifiable Attributes -----------------

    @property
    @fail_if_deleted
    def name(self) -> str:
        """The name of the session."""
        return self._name

    @name.setter
    @fail_if_session_currently_exists
    def name(self, value: str):
        self._name = value

    @property
    @fail_if_deleted
    def cluster_id(self) -> str:
        """The name of the cluster the session is running on.
        """
        return self._cluster_id

    @cluster_id.setter
    @fail_if_session_currently_exists
    def cluster_id(self, value: str):
        self._cluster_id = value

    @property
    @fail_if_deleted
    def datastores(self) -> Dict[str, Datastore]:
        """mapping of mount directories to `Datastore` objects attached to the session.

        For example; a datastore mounted to the path `/mydata/mnist` would return
        `{"/mydata/mnist": Datastore(...)}`
        """
        return self._datastores

    @datastores.setter
    @fail_if_session_currently_exists
    def datastores(self, value: Dict[str, Datastore]):
        self._datastores = value

    @property
    @fail_if_deleted
    def disk_size_gb(self) -> str:
        """The size of the home directory disk to spin up
        """
        return self._disk_size_gb

    @disk_size_gb.setter
    @fail_if_session_currently_exists
    def disk_size_gb(self, value: str):
        self._disk_size_gb = value

    @property
    @fail_if_deleted
    def instance_type(self) -> str:
        """The type of the virtual machine used on the compute cluster when running the session.
        """
        return self._instance_type

    @instance_type.setter
    @fail_if_session_currently_exists
    def instance_type(self, value: str):
        self._instance_type = value

    @property
    @fail_if_deleted
    def use_spot(self) -> bool:
        """If a spot instance type is used to spin up the session.
        """
        return self._use_spot

    @use_spot.setter
    @fail_if_session_currently_exists
    def use_spot(self, value: bool):
        self._use_spot = value

    # ----------------------- Fixed Attributes ---------------------------

    @property
    @fail_if_deleted
    def hourly_cost(self) -> float:
        """The per hour cost of this session configuration when it is in a 'RUNNING' state.
        """
        return self._hourly_cost

    @property
    @fail_if_deleted
    def total_cost(self) -> float:
        """The total cost of the session over it's entire lifetime.
        """
        return self._total_cost

    @property
    @fail_if_deleted
    def total_run_time(self) -> float:
        """How long the session has run for (not including paused time) in second.
        """
        return self._total_run_time

    @property
    @fail_if_deleted
    def desired_state(self) -> V1SessionState:
        """The state of the system we are trying to achieve.

        This might be one of 'PENDING', 'RUNNING', 'PAUSED'
        """
        return self._desired_state

    @property
    @fail_if_deleted
    def last_status_state(self) -> V1SessionState:
        """The last recorded state of the session instance on the grid platform.

        This might be one of 'PENDING', 'RUNNING', 'PAUSED'
        """
        return self._last_status_state

    @property
    @fail_if_deleted
    def created_at(self) -> datetime:
        """The timestamp when the session was first created.
        """
        return self._created_at

    @property
    @fail_if_deleted
    def started_at(self) -> datetime:
        """The timestamp when the session was last started.
        """
        return self._started_at

    @property
    @fail_if_deleted
    def finished_at(self) -> datetime:
        """The timestamp when the session was last stopped.
        """
        return self._finished_at

    @property
    @fail_if_deleted
    def last_state_status_transition_at(self) -> datetime:
        """The last timestamp when the session's running state was changed.
        """
        return self._last_state_status_transition_at

    @property
    @fail_if_deleted
    def jupyter_lab_url(self) -> str:
        """URL to access the jupyterlab server at over the public internet.
        """
        return self._jupyter_lab_url

    @property
    @fail_if_deleted
    def jupyter_lab_token(self) -> str:
        """Security token required to access this session over the public internet.
        """
        return self._jupyter_lab_token

    @property
    @fail_if_deleted
    def ssh_url(self) -> str:
        """URL used to SSH into this session.
        """
        return self._ssh_url

    @property
    @fail_if_deleted
    def user(self) -> User:
        """Details of the user who is the creator of this session.
        """
        return self._user

    @property
    def currently_exists(self) -> bool:
        """If this object refers to a session which has been created on the grid platform.

        Prior to calling `start` for the frist time, the grid platform has not created
        the actual session implementation, and the object does not exist.
        """
        return self._currently_exists

    # ---------------------- Interaction Methods -----------------------------------

    def start(self):
        """Start an interactive session based on this configuration.

        If the session does not exist, a new session will be created; if the session
        exists, but is paused, then the session will be resumed; if the session exists
        and is already running, no action will be taken.
        """
        if self._currently_exists is True:
            session = resume_session(self._client, name=self._name, cluster_id=self._cluster_id)
            session_id = session.id
        else:
            session_id = create_session(
                self._client,
                name=self._name,
                instance_type=self._instance_type,
                cluster_id=self._cluster_id,
                datastores=self._datastores,
                disk_size_gb=self._disk_size_gb,
                use_spot=self._use_spot
            )

        self._id = session_id
        self._setup_from_existing()

    @fail_if_deleted
    @fail_if_session_does_not_exist
    def pause(self):
        """Pauses a session which is currently running.

        Pausing a session stops the running instance (and any computations being
        performed on it - be sure to save your work!) and and billing of your account
        for the machine. The session can be resumed at a later point with all your
        persisted files and saved work unchanged.
        """
        pause_session(self._client, name=self._name, cluster_id=self._cluster_id)
        self._setup_from_existing()

    @fail_if_deleted
    @fail_if_session_does_not_exist
    def delete(self):
        """Deletes a session which is either running or paused.

        Deleting a session will stop the running instance (and any computations being
        performed on it) and billing of your account. All work done on the machine
        is permenantly removed, including all/any saved files, code, or downloaded
        data (assuming the source of the data was not a grid datastore - datastore
        data is not deleted).
        """
        delete_session(self._client, name=self._name, cluster_id=self._cluster_id)
        self._setup_from_existing()
        self._alive = False

    @fail_if_deleted
    @fail_if_session_does_not_exist
    def change_instance_type(self, instance_type: str, use_spot: Optional[bool] = None):
        """Change the instance type of a session.

        The session must be paused before calling this method.

        Parameters
        ----------
        instance_type
            the new instance type the session node should use.
        use_spot
            if true, use interuptable spot instances (which come at a steap discount,
            but which can be interrupted and shut down at any point in time depending
            on cloud provider instance type demand). If false, use an on-demand instance.

            By default this value is None, indicating that no change will be made to the
            current configuratoin.
        """
        self._setup_from_existing()
        if self.last_status_state != V1SessionState.PAUSED:
            raise RuntimeError("session must be paused before calling `change_instance_type`.")

        change_session_instance_type(
            self._client, name=self._name, instance_type=instance_type, use_spot=use_spot, cluster_id=self._cluster_id
        )
        self._setup_from_existing()

    def _setup_from_existing(self):
        if self._id is None:
            self._alive = False
            self._currently_exists = False
            return

        session = get_session(self._client, session_id=self._id)
        spec: V1SessionSpec = session.spec
        status: V1SessionStatus = session.status

        self._cluster_id = spec.cluster_id

        self._instance_type = spec.instance_type
        self._disk_size_gb = spec.resources.storage_gb
        self._use_spot = spec.use_spot
        self._datastores: Dict[str, Datastore] = {}

        for dstore_input in spec.datastores:
            dstore_input: V1DatastoreInput

            datastore_id = datastore_id_from_dsn(dstore_input.dsn)
            dstore_def = get_datastore(self._client, datastore_id=datastore_id, cluster_id=spec.cluster_id)
            datastore = Datastore(
                name=dstore_def.name, version=dstore_def.spec.version, cluster_id=dstore_def.spec.cluster_id
            )
            self._datastores[dstore_input.mount_path] = datastore

        self._hourly_cost = session.hourly_cost
        self._total_cost = session.cost
        self._total_run_time = status.total_run_time_seconds

        self._desired_state = spec.desired_state
        self._last_status_state = status.phase

        self._created_at = session.created_at
        self._started_at = status.start_timestamp
        self._finished_at = status.stop_timestamp
        self._last_state_status_transition_at = status.last_state_status_transition_timestamp

        self._jupyter_lab_url = status.jupyter_lab_url
        self._jupyter_lab_token = status.jupyter_lab_token
        self._ssh_url = status.ssh_url

        # TODO: complete with owner's username, first name, & last name
        local_user = user_from_logged_in_account()
        if spec.user_id == local_user.user_id:
            self._user = local_user
        elif spec.user_id is None:
            self._user = local_user
        else:
            teams = get_teams()
            for team in teams.values():
                for user_id, user in team.members.items():
                    if user_id == spec.user_id:
                        self._user = user

        self._alive = True
        self._currently_exists = True
