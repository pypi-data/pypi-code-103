from typing import TYPE_CHECKING

import datetime

from hoss.api import CoreAPI
from hoss.ref import DatasetRef
import hoss.error

if TYPE_CHECKING:
    from hoss.namespace import Namespace

PERM_NONE = None
PERM_READ = "r"
PERM_READ_WRITE = "rw"


class Dataset(CoreAPI, DatasetRef):
    def __init__(self, namespace: 'Namespace', dataset_name: str, description: str,
                 created_on: datetime.datetime,
                 root_directory: str, owner: str, bucket: str, permissions: dict):
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.description = description
        self.created_on = created_on
        self.root_directory = root_directory
        self.owner = owner
        self.bucket = bucket
        self.permissions = permissions

        CoreAPI.__init__(self, server_url=self.namespace.base_url, auth_instance=namespace.auth)
        DatasetRef.__init__(self, namespace=self.namespace, parent=None, dataset_name=dataset_name,
                            key=root_directory, name='', etag=None, last_modified=None, size_bytes=None)

    def __repr__(self):
        return f"<Dataset: {self.namespace} - {self.dataset_name}"

    def display(self):
        """Helper to print some useful info about the dataset"""
        print("--Dataset------")
        print(f"Name: {self.dataset_name}")
        print(f"Description: {self.description}")
        print(f"Namespace: {self.namespace}")
        print(f"Created On: {self.created_on}")
        print(f"Root Directory: {self.root_directory}")
        print(f"Owner: {self.owner}")
        print("Permissions:")
        for u, p in self.permissions.items():
            print(f"\t{u}: {p}")
        print("---------------")
        return self

    def is_sync_enabled(self) -> bool:
        """Check if sync is enabled for the dataset"""
        response = self._request("GET", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync")
        return response

    def enable_sync(self, sync_type: str) -> None:
        """Method to enable syncing on a dataset. The namespace must also already have syncing enabled.

        If the namespace is configured with duplex syncing, you can set the dataset to either simplex or duplex
        If the namespace is configured with only simplex syncing, you can only set the dataset to simplex

        Note - currently syncing only will sync objects mutated after syncing is enabled.

        Args:
            sync_type: type of sync config (`simplex` or `duplex`)

        Returns:
            None
        """
        if sync_type not in ["simplex", "duplex"]:
            raise hoss.error.HossException(f"'sync_type' must be either 'simplex' or 'duplex'")

        data = {"sync_type": sync_type}
        self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync", json=data)

    def disable_sync(self) -> None:
        """Disable dataset syncing

        Returns:
            None
        """
        self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync")

    # Dataset admin methods
    def set_user_permission(self, username, permission):
        """Set permissions on the dataset for a user.

        This will attach the user's "personal" group under the hood.

        Args:
            username: username for the user you wish to set
            permission: permission level ('r', 'rw', or None)

        Returns:

        """
        if permission == PERM_NONE:
            self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/user/{username}")
            del self.permissions[username + "-hoss-default-group"]
        else:
            self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/user/{username}/access/{permission}")
            self.permissions[username + "-hoss-default-group"] = permission
        return self
    
    def set_group_permission(self, group_name, permission):
        """Set permissions on the dataset for a groupd.

        This will attach the user's "personal" group under the hood.

        Args:
            group_name: group you wish to set
            permission: permission level ('r', 'rw', or None)

        Returns:

        """
        if permission == PERM_NONE:
            self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/group/{group_name}")
            del self.permissions[group_name]
        else:
            self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/group/{group_name}/access/{permission}")
            self.permissions[group_name] = permission
        return self
