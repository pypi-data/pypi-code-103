from typing import Optional, List, Dict

import hoss
from hoss.error import *
from hoss.auth import AuthService
from hoss.namespace import Namespace
from hoss.objectstore import ObjectStore
from hoss.api import CoreAPI


class CoreService(CoreAPI):
    def __init__(self, server_url, auth_instance: Optional[AuthService] = None):
        """A class to interact with the Hoss core service

        Args:
            server_url: root URL to the server, including the protocol
            auth_instance: an optional AuthService instance that will be used instead of using the server_url to
             instantiate one
        """
        super().__init__(server_url, auth_instance)

    def __repr__(self):
        return f"<Hoss Server: {self.base_url}>"

    def _populate_object_store(self, api_response: dict) -> ObjectStore:
        return ObjectStore(api_response.get('name'),
                           api_response.get('description'),
                           api_response.get('endpoint'),
                           api_response.get('type'),
                           self.base_url,
                           self.auth)

    def list_object_stores(self):
        """List Object Stores within the Server

        Returns:
            list of object store instances
        """
        response = self._request("GET", f"/object_store/")
        return [self._populate_object_store(n) for n in response]

    def get_object_store(self, name: str):
        """Get Object Stores by name

        Returns:
            list of object store instances
        """
        response = self._request("GET", f"/object_store/{name}")
        return self._populate_object_store(response)

    def _populate_namespace(self, api_response: dict) -> Namespace:
        return Namespace(self.base_url, api_response.get('name'), api_response.get('bucket_name'),
                         api_response.get('description'),
                         self._populate_object_store(api_response.get('object_store')),
                         self.auth)

    def list_namespaces(self) -> List[Namespace]:
        """List Namespaces within the Server

        Returns:
            list of namespace instances
        """
        response = self._request("GET", f"/namespace/")
        return [self._populate_namespace(n) for n in response]

    def get_namespace(self, name) -> Namespace:
        """Get a namespace by name

        Returns:
            list of namespace instances
        """
        response = self._request("GET", f"/namespace/{name}")
        return self._populate_namespace(response)

    def create_namespace(self, name: str, description: str, object_store_name: str, bucket_name: str) -> Namespace:
        """Create a new namespace

        Args:
            name: name of the namespace
            description: description of the namespace
            object_store_name: name of the object store the namespace uses
            bucket_name: name of the bucket in the object store

        Returns:
            Namespace instance
        """
        data = {"name": name, "description": description,
                "object_store_name": object_store_name, "bucket_name": bucket_name}
        response = self._request("POST", f"/namespace/", json=data)
        return self._populate_namespace(response)

    def delete_namespace(self, name: str) -> None:
        """Delete a namespace. It must be empty to delete

        Args:
            name: name of the namespace

        Returns:
            None
        """
        dataset_list = self._request("GET", f"/namespace/{name}/dataset/")
        if len(dataset_list) > 0:
            raise HossException(f"The namespace '{name}' contains {len(dataset_list)} dataset. "
                               f"Namespace must be empty to delete")
        self._request("DELETE", f"/namespace/{name}")
        return

    def search(self, metadata: Dict[str, str], namespace: Optional[str] = None, dataset: Optional[str] = None,
               modified_before: Optional[str] = None, modified_after: Optional[str] = None,
               limit: Optional[int] = 25, offset: Optional[int] = 0) -> List:
        """Search a server for objects

        Args:
            metadata: dictionary of key-value pairs that must match
            namespace: name of namespace to filter results
            dataset: name of dataset to filter results (namespace must be set
                along with dataset to be valid)
            modified_before: datetime string format `2006-01-02T15:04:05.000Z` to filter results
            modified_after: datetime string format `2006-01-02T15:04:05.000Z` to filter results
            limit: number of items to return per page
            offset: starting point in the index for returned items

        Returns:
            Raw response
        """
        query_params = []

        # add metadata key pairs
        metadata_params = [f"{k}:{metadata[k]}" for k in metadata]
        if metadata_params:
            query_params.append("metadata=" + ",".join(metadata_params).lower())

        # add namespace and dataset filters
        if namespace:
            query_params.append(f"namespace={namespace}")
            if dataset:
                query_params.append(f"dataset={dataset}")
        elif dataset:
            raise HossException("Must provide a namespace if searching within a specific dataset")
        
        # add time range filters
        if modified_before:
            query_params.append(f"modified_before={modified_before}")
        if modified_after:
            query_params.append(f"modified_after={modified_after}")

        # add pagination
        query_params.append(f"size={limit}")
        query_params.append(f"from={offset}")

        query_param_str = "&".join(query_params)

        # Remember all metadata headers are case insensitive, so we lowercase everything
        response = self._request("GET", f"/search?{query_param_str}")
        return response['results']

    def search_refs(self, metadata: Dict[str, str], namespace: Optional[str] = None, dataset: Optional[str] = None,
                    modified_before: Optional[str] = None, modified_after: Optional[str] = None,
                    limit: Optional[int] = 25, offset: Optional[int] = 0) -> List:

        results = self.search(metadata, namespace, dataset, modified_before, modified_after, limit, offset)
        return [hoss.resolve(result["uri"], self.auth) for result in results]
