from typing import Dict, List, Optional

from grid.openapi import (
    Body1,
    Externalv1Session,
    V1CreateSessionRequest,
    V1CreateSessionResponse,
    V1DatastoreInput,
    V1DeleteSessionResponse,
    V1GetSessionResponse,
    V1ListSessionsResponse,
    V1Resources,
    V1SessionSpec,
    V1SessionState,
    V1UpdateSessionResponse,
)
from grid.sdk.datastore import Datastore
from grid.sdk.rest.client import GridRestClient
from grid.sdk.rest.datastores import datastore_dsn_from_id


def session_id_from_name(c: GridRestClient, name: str, cluster_id: Optional[str] = None) -> str:
    """Find the id of a session with some name on a cluster.

    Parameters
    ----------
    c
        Client
    name
        the name of the session to find the ID of
    cluster_id
        which cluster should be used to find the datastore in.

    Returns
    -------
    str
       The ID of the session.
    """
    if cluster_id is None:
        sessions: V1ListSessionsResponse = c.session_service_list_sessions(
            phase_in=[V1SessionState.RUNNING, V1SessionState.PAUSED, V1SessionState.PENDING]
        )
    else:
        sessions: V1ListSessionsResponse = c.session_service_list_sessions(
            cluster_id=cluster_id, phase_in=[V1SessionState.RUNNING, V1SessionState.PAUSED, V1SessionState.PENDING]
        )

    for session in sessions.sessions:
        session: Externalv1Session
        if session.name == name:
            return session.id

    raise KeyError(f"could not find session with name {name} in " f"sessions: {[s.name for s in sessions.sessions]}")


def list_sessions(c: GridRestClient,
                  cluster_id: Optional[str] = None,
                  user_ids: Optional[List[str]] = None) -> List[Externalv1Session]:
    kwargs = {}
    if cluster_id is not None:
        kwargs['cluster_id'] = cluster_id
    if user_ids is not None:
        kwargs['user_ids'] = user_ids

    resp: V1ListSessionsResponse = c.session_service_list_sessions(**kwargs)
    return resp.sessions


def get_session(c: GridRestClient, session_id: str) -> Externalv1Session:
    return c.session_service_get_session(id=session_id)


def create_session(
    c: GridRestClient,
    name: str,
    instance_type: str,
    cluster_id: Optional[str] = None,
    datastores: Optional[Dict[str, Datastore]] = None,
    disk_size_gb: str = '200',
    use_spot: bool = False
) -> str:
    """Create a session on the grid platform.

    Parameters
    ----------
    c
        API client
    name
        human readable name of the session which is created
    instance_type
        cloud provider instance type used to start the session on.
    cluster_id
        cluster ID to start the session on
    disk_size_gb
        The size of the disk to use.
    datastores
        mapping of mount paths to datastores
    use_spot
        if we should use a spot instance or not.

    Returns
    -------
    str
        ID of the session which was created.
    """
    if datastores is None:
        datastores = {}

    dstores = []
    for mount_path, datastore in datastores.items():
        dstore = V1DatastoreInput(dsn=datastore_dsn_from_id(id=datastore.datastore_id), mount_path=mount_path)
        dstores.append(dstore)

    request = V1CreateSessionRequest(
        name=name,
        spec=V1SessionSpec(
            cluster_id=cluster_id,
            use_spot=use_spot,
            desired_state=V1SessionState.RUNNING,
            instance_type=instance_type,
            datastores=dstores,
            resources=V1Resources(storage_gb=disk_size_gb, )
        )
    )

    resp: V1CreateSessionResponse = c.session_service_create_session(request)

    return resp.id


def pause_session(c: GridRestClient, name: str, cluster_id: Optional[str] = None) -> str:
    """Pause a session with a given name.

    Parameters
    ----------
    c
        Open API client
    name
        name of the session to pause
    cluster_id
        cluster containing the session which will be paused

    Returns
    -------
    str
        ID of the session which is paused.
    """
    session_id = session_id_from_name(c, cluster_id=cluster_id, name=name)

    session: V1GetSessionResponse = c.session_service_get_session(id=session_id)
    spec: V1SessionSpec = session.spec
    spec.desired_state = V1SessionState.PAUSED

    resp: V1UpdateSessionResponse = c.session_service_update_session(
        id=session.id,
        # TODO: Why is this named `Body1` in the openapi spec?
        body=Body1(name=name, spec=spec)
    )
    return resp.id


def delete_session(c: GridRestClient, name: str, cluster_id: Optional[str] = None) -> V1DeleteSessionResponse:
    """Delete a session with a given name.

    Parameters
    ----------
    c
        Open API client
    name
        name of the session to pause
    cluster_id
        cluster containing the session which will be deleted

    Returns
    -------
    str
        ID of the session which is deleted.
    """
    session_id = session_id_from_name(c, cluster_id=cluster_id, name=name)
    c.session_service_delete_session(id=session_id)
    return session_id


def resume_session(c: GridRestClient, name: str, cluster_id: Optional[str] = None) -> V1UpdateSessionResponse:
    """Resumes a session with a given name.

    Parameters
    ----------
    c
        Open API client
    name
        name of the session to pause
    cluster_id
        cluster containing the session which will be resumed

    Returns
    -------
    V1UpdateSessionResponse
        session which is resumed
    """
    session_id = session_id_from_name(c, cluster_id=cluster_id, name=name)

    session: V1GetSessionResponse = c.session_service_get_session(id=session_id)
    spec: V1SessionSpec = session.spec
    spec.desired_state = V1SessionState.RUNNING
    session.spec = spec
    resp: V1UpdateSessionResponse = c.session_service_update_session(
        id=session_id, body=Body1(name=session.name, spec=spec)
    )
    return resp


def change_session_instance_type(
    c: GridRestClient,
    name: str,
    instance_type,
    use_spot: Optional[bool] = None,
    cluster_id: Optional[str] = None
) -> V1UpdateSessionResponse:
    """Change the instance type of a session.

    Parameters
    ----------
    c
        Open API Client
    name
        name of the session to alter
    instance_type
        new instance type to use for the session
    use_spot
        if true, use interuptable spot instances (which come at a steap discount,
        but which can be interrupted and shut down at any point in time depending
        on cloud provider instance type demand). If false, use an on-demand instance.

        By default this value is None, indicating that no change will be made to the
        current configuratoin.
    cluster_id
        cluster ID of the session to change the instance type of

    Returns
    -------
    V1UpdateSessionResponse
        response from the server
    """
    session_id = session_id_from_name(c, cluster_id=cluster_id, name=name)

    session = get_session(c, session_id=session_id)
    session.spec.instance_type = instance_type
    if use_spot is not None:
        session.spec.use_spot = use_spot

    result = c.session_service_update_session(
        id=session.id,
        # TODO: rename... This is V1UpdateSessionRequest
        body=Body1(name=session.name, spec=session.spec),
    )
    return result
