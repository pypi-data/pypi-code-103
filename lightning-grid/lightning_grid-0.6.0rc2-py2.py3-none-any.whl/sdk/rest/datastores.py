from typing import Dict, Optional

from grid.openapi import Externalv1Datastore, Externalv1DatastoreSpec, V1GetDatastoreResponse, V1ListDatastoresResponse
from grid.sdk.rest.client import GridRestClient


def datastore_id_from_name(c: GridRestClient, cluster_id: str, name: str, version: Optional[str] = None) -> str:
    """Find the id of a datastore with some name (and optionally version) on a cluster.

    Parameters
    ----------
    c
        Client
    cluster_id
        which cluster should be used to find the datastore in.
    name
        the name of the datastore to find the ID of
    version
        The version of the datastore with ``name`` to find the ID of.
        NOTE: If no ``version`` argument is present, then the maximum
        version of the datastore will be used.

    Returns
    -------
    str
       The ID of the datastore.
    """
    dstores: V1ListDatastoresResponse = c.datastore_service_list_datastores(cluster_id=cluster_id, available=True)

    datastore_versions: Dict[str, Externalv1Datastore] = {}

    for dstore in dstores.datastores:
        dstore: Externalv1Datastore
        if dstore.name == name:
            spec: Externalv1DatastoreSpec = dstore.spec
            datastore_versions[spec.version] = dstore

    if version is None:
        # use the max version available
        version = max(datastore_versions.keys())

    try:
        return datastore_versions[version].id
    except KeyError:
        raise KeyError(f"no datastore exists with name: {name}")


def get_datastore(c: GridRestClient, datastore_id: str, cluster_id: str) -> V1GetDatastoreResponse:
    dstore: V1GetDatastoreResponse = c.datastore_service_get_datastore(cluster_id=cluster_id, id=datastore_id)
    return dstore


def datastore_dsn_from_id(id: str) -> str:
    """Return the DSN of the datastore

    Parameters
    ----------
    id
        datastore ID to convert into DSN.

    Returns
    -------
    str
        DSN form of the datastore ID.
    """
    return f"datastore://grid/{id}"


def datastore_id_from_dsn(dsn: str) -> str:
    """Return the id of a datastore from a DSN.

    Parameters
    ----------
    dsn
        DSN string to convert into an ID

    Returns
    -------
    str
        ID of the datastore DSN string.
    """
    # convert ``datastore://grid/{id}`` -> ``['datastore:', '', 'grid', '{id}']``
    # convert ``datastore://grid/{id}/`` -> ``['datastore:', '', 'grid', '{id}', '']``
    # ... (we want the last element)
    parts = dsn.split('/')
    if dsn.endswith('/'):
        if len(parts) < 2:
            raise RuntimeError(f"Internal Error. invalid datastore dsn format while parsing ID. dsn={dsn}")
        return parts[-2]
    return parts[-1]
