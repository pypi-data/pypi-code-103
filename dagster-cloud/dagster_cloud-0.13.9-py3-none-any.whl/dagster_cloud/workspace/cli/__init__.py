import time
from pathlib import Path

import yaml
from dagster import check
from dagster.serdes.serdes import deserialize_json_to_dagster_namedtuple
from dagster.utils import DEFAULT_WORKSPACE_YAML_FILENAME
from dagster_cloud.workspace.config_schema import process_workspace_config
from dagster_cloud.workspace.origin import CodeDeploymentMetadata
from typer import Argument, Option, Typer

from ...cli import gql, ui
from ...cli.config_utils import dagster_cloud_options
from ...cli.utils import add_options

app = Typer(help="Commands for managing a dagster cloud workspace.")

_DEPLOYMENT_METADATA_OPTIONS = {
    "image": (str, Option(None, "--image", help="Docker image.")),
    "python_file": (
        Path,
        Option(
            None, "--python-file", "-f", exists=False, help="Python file where repository lives."
        ),
    ),
    "package_name": (
        str,
        Option(None, "--package-name", "-p", help="Python package where repositories live"),
    ),
}

ADD_LOCATION_MUTATION = """
mutation ($location: LocationSelector!) {
   addLocation(location: $location) {
      __typename
      ... on WorkspaceEntry {
        locationName
      }
      ... on PythonError {
        message
        stack
      }
   }
}
"""

REPOSITORY_LOCATIONS_QUERY = """
{
  workspaceOrError {
    __typename
    ... on Workspace {
      locationEntries {
        __typename
        name
        loadStatus
        locationOrLoadError {
          __typename
          ... on RepositoryLocation {
            name
          }
          ... on PythonError {
              message
              stack
          }
        }
      }
    }
    ... on PythonError {
      message
      stack
    }
  }
}
"""


@app.command(
    name="add-location",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
@add_options(_DEPLOYMENT_METADATA_OPTIONS)
def add_command(
    api_token: str,
    url: str,
    location: str = Argument(..., help="Code location name."),
    **kwargs,
):
    """Add a new repository location to the workspace."""
    client = gql.graphql_client_from_url(url, api_token)
    execute_add_command(client, location, kwargs)


def _get_location_input(location, kwargs):
    location_input = {"name": location}

    python_file = kwargs.get("python_file")
    package_name = kwargs.get("package_name")

    if (not python_file and not package_name) or (python_file and package_name):
        raise ui.error("Must specify exactly one of --python-file or --package-name.")

    if python_file:
        location_input["pythonFile"] = str(python_file)
    if package_name:
        location_input["packageName"] = package_name
    if "image" in kwargs:
        location_input["image"] = kwargs["image"]

    return location_input


def execute_add_command(client, location, kwargs):
    variables = {"location": _get_location_input(location, kwargs)}

    ui.print(f"Adding location {location}...")

    add_res = client.execute(ADD_LOCATION_MUTATION, variable_values=variables)

    if add_res["data"]["addLocation"]["__typename"] == "WorkspaceEntry":
        ui.print(f"Added location {location}.")
    else:
        raise ui.error(f"Unable to add location: {str(add_res)}")

    wait_for_load(client, [location])


def _get_locations(client):
    repo_locations_res = client.execute(REPOSITORY_LOCATIONS_QUERY)

    if not "data" in repo_locations_res:
        raise ui.error(f"Unable to fetch locations: {str(repo_locations_res)}")
    locations_or_error = repo_locations_res["data"]["workspaceOrError"]
    if locations_or_error["__typename"] == "PythonError" or not "data":
        raise ui.error(f"Unable to fetch locations: {str(locations_or_error)}")

    return repo_locations_res["data"]["workspaceOrError"]["locationEntries"]


def wait_for_load(client, locations):
    start_time = time.time()
    ui.print(f"Waiting for agent to sync changes to {','.join(locations)}...")
    while True:
        if time.time() - start_time > 300:
            raise ui.error("Timed out waiting for location data to update")

        nodes = _get_locations(client)

        nodes_by_location = {node["name"]: node for node in nodes}

        if all(
            location in nodes_by_location
            and nodes_by_location[location].get("loadStatus") == "LOADED"
            for location in locations
        ):

            error_locations = [
                location
                for location in locations
                if "locationOrLoadError" in nodes_by_location[location]
                and nodes_by_location[location]["locationOrLoadError"]["__typename"]
                == "PythonError"
            ]

            if error_locations:
                error_string = "Some locations failed to load after being synced by the agent:\n" + "\n".join(
                    [
                        f"Error loading {error_location}: {str(nodes_by_location[error_location]['locationOrLoadError'])}"
                        for error_location in error_locations
                    ]
                )
                raise ui.error(error_string)
            else:
                ui.print(
                    f"Agent synced changes to {','.join(locations)}. Changes should now be visible in dagit."
                )
                break

        time.sleep(3)


UPDATE_LOCATION_MUTATION = """
mutation ($location: LocationSelector!) {
   updateLocation(location: $location) {
      __typename
      ... on WorkspaceEntry {
        locationName
      }
      ... on PythonError {
        message
        stack
      }
   }
}
"""


@app.command(
    name="update-location",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
@add_options(_DEPLOYMENT_METADATA_OPTIONS)
def update_command(
    api_token: str,
    url: str,
    location: str = Argument(..., help="Code location name."),
    upsert: bool = Option(
        False, help="Whether to create the repository location if it does not exist."
    ),
    **kwargs,
):
    """Update the image for a repository location in the workspace."""
    client = gql.graphql_client_from_url(url, api_token)
    execute_update_command(client, location, upsert, kwargs)


def execute_update_command(client, location, upsert, kwargs):
    if upsert:
        locations = [location["name"] for location in _get_locations(client)]

        if not location in locations:
            execute_add_command(client, location, kwargs)
            return

    ui.print(f"Updating location {location}...")

    variables = {"location": _get_location_input(location, kwargs)}

    update_res = client.execute(UPDATE_LOCATION_MUTATION, variable_values=variables)

    if update_res["data"]["updateLocation"]["__typename"] == "WorkspaceEntry":
        ui.print(f"Updated location {location}.")
    else:
        raise ui.error(f"Unable to update location: {str(update_res)}")

    wait_for_load(client, [location])


DELETE_LOCATION_MUTATION = """
mutation ($locationName: String!) {
   deleteLocation(locationName: $locationName) {
      __typename
      ... on DeleteLocationSuccess {
        locationName
      }
      ... on PythonError {
        message
        stack
      }
   }
}
"""


@app.command(
    name="delete-location",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
def delete_command(
    api_token: str,
    url: str,
    location: str = Argument(..., help="Code location name."),
):
    """Delete a repository location from the workspace."""
    client = gql.graphql_client_from_url(url, api_token)
    execute_delete_command(client, location)


def execute_delete_command(client, location):
    ui.print(f"Deleting location {location}...")

    variables = {"locationName": location}

    delete_res = client.execute(DELETE_LOCATION_MUTATION, variable_values=variables)

    if delete_res["data"]["deleteLocation"]["__typename"] == "DeleteLocationSuccess":
        ui.print(f"Deleted location {location}")
    else:
        raise ui.error(f"Unable to delete location: {str(delete_res)}")


LIST_LOCATIONS_QUERY = """
query WorkspaceEntries {
    workspace {
        workspaceEntries {
            locationName
            serializedDeploymentMetadata
        }
    }
}
"""


@app.command(
    name="list",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
def list_command(
    url: str,
    api_token: str,
):
    """List repository locations in the workspace."""
    client = gql.graphql_client_from_url(url, api_token)
    execute_list_command(client)


def execute_list_command(client):
    list_res = client.execute(LIST_LOCATIONS_QUERY)

    ui.print("Listing locations...")

    for location in list_res["data"]["workspace"]["workspaceEntries"]:
        metadata = check.inst(
            deserialize_json_to_dagster_namedtuple(location["serializedDeploymentMetadata"]),
            CodeDeploymentMetadata,
        )

        location_desc = [location["locationName"]]
        if metadata.python_file:
            location_desc.append(f"File: {metadata.python_file}")
        if metadata.package_name:
            location_desc.append(f"Package: {metadata.package_name}")
        if metadata.image:
            location_desc.append(f"Image: {metadata.image}")

        ui.print("\t".join(location_desc))


RECONCILE_LOCATIONS_MUTATION = """
mutation ($locations: [LocationSelector]!) {
    reconcileLocations(locations: $locations) {
        __typename
        ... on ReconcileLocationsSuccess {
            locations {
                locationName
            }
        }
        ... on PythonError {
            message
            stack
        }
    }
}
"""


@app.command(name="sync")
@dagster_cloud_options(allow_empty=True, requires_url=True)
def sync_command(
    url: str,
    api_token: str,
    workspace: Path = Option(
        DEFAULT_WORKSPACE_YAML_FILENAME,
        "--workspace",
        "-w",
        exists=True,
        help="Path to workspace file.",
    ),
):
    """"Sync the workspace with the contents of a workspace.yaml file."""
    client = gql.graphql_client_from_url(url, api_token)
    execute_sync_command(client, workspace)


def execute_sync_command(client, workspace):
    with open(str(workspace), "r") as f:
        config = yaml.load(f.read(), Loader=yaml.SafeLoader)
        process_workspace_config(config)

    locations = {"locations": []}
    for name, metadata in config["locations"].items():
        locations["locations"].append(
            {
                "name": name,
                "image": metadata.get("image"),
                "packageName": metadata.get("package_name"),
                "pythonFile": metadata.get("python_file"),
            }
        )

    reconcile_res = client.execute(RECONCILE_LOCATIONS_MUTATION, variable_values=locations)

    if reconcile_res["data"]["reconcileLocations"]["__typename"] == "ReconcileLocationsSuccess":
        locations = sorted(
            [
                location["locationName"]
                for location in reconcile_res["data"]["reconcileLocations"]["locations"]
            ]
        )
        ui.print(f"Synced locations: {', '.join(locations)}")
    else:
        raise ui.error(f"Unable to sync locations: {str(reconcile_res)}")

    wait_for_load(client, locations)
