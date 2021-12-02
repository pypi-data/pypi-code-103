# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

import json
from typing import Optional
from uuid import UUID

from ariadne import MutationType
from graphql.type.definition import GraphQLResolveInfo

from madam.domains.application import MainApplication

mutation = MutationType()


@mutation.field("createWorkflow")
def resolve_create_workflow(_, info: GraphQLResolveInfo, content: str):
    """
    Create workflow from BPMN XML content

    :param _: Parent
    :param info: Context
    :param content: BPMN XML content
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        workflow = application.workflows.create(content)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True, "workflow": workflow}


@mutation.field("deleteWorkflow")
def resolve_delete_workflow(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Delete workflow

    :param _: Parent
    :param info: Context
    :param id: Workflow ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        workflow = application.workflows.read(id)
        application.workflows.delete(workflow)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("startWorkflow")
def resolve_start_workflow(
    _,
    info: GraphQLResolveInfo,
    id: str,
    version: Optional[int],
    variables: Optional[str],
):  # pylint: disable=redefined-builtin
    """
    Start an instance of workflow ID

    :param _: Parent
    :param info: Context
    :param id: Workflow ID
    :param version: Workflow version
    :param variables: Workflow initial variables
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    if variables is not None:
        variables_obj = json.loads(variables)
    else:
        variables_obj = variables
    try:
        result = application.workflows.start(id, version, variables_obj)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": result}


@mutation.field("abortWorkflow")
def resolve_abort_workflow(
    _, info: GraphQLResolveInfo, id: str, version: Optional[int]
):  # pylint: disable=redefined-builtin
    """
    Abort all instances of workflow ID

    :param _: Parent
    :param info: Context
    :param id: Workflow ID
    :param version: Workflow version
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        result = application.workflows.abort(id, version)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": result}


@mutation.field("abortWorkflowInstance")
def resolve_abort_workflow_instance(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Abort workflow instance by ID

    :param _: Parent
    :param info: Context
    :param id: Workflow instance ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    workflow_instance = application.workflow_instances.read(UUID(id))

    try:
        application.workflow_instances.abort(workflow_instance)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("deleteWorkflowInstance")
def resolve_delete_workflow_instance(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Delete workflow instance

    :param _: Parent
    :param info: Context
    :param id: Workflow instance ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        workflow_instance = application.workflow_instances.read(UUID(id))
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    try:
        application.workflow_instances.delete(workflow_instance)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("abortWorkflowInstancesByWorkflow")
def resolve_abort_workflow_instances_by_workflow(
    _, info: GraphQLResolveInfo, id: str, version: Optional[int]
):  # pylint: disable=redefined-builtin
    """
    Abort workflow instances of workflow id and version

    :param _: Parent
    :param info: Context
    :param id: Workflow instance ID
    :param version: Workflow version
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        workflow = application.workflows.read(id, version)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    try:
        application.workflow_instances.abort_by_workflow(workflow)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("deleteWorkflowInstancesByWorkflow")
def resolve_delete_workflow_instances_by_workflow(
    _, info: GraphQLResolveInfo, id: str, version: Optional[int]
):  # pylint: disable=redefined-builtin
    """
    Delete workflow instances of workflow id and version

    :param _: Parent
    :param info: Context
    :param id: Workflow instance ID
    :param version: Workflow version
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        workflow = application.workflows.read(id, version)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    try:
        application.workflow_instances.delete_by_workflow(workflow)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("abortTimer")
def resolve_abort_timer(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Abort timer by ID

    :param _: Parent
    :param info: Context
    :param id: Timer ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        application.timers.abort(UUID(id))
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("deleteTimer")
def resolve_delete_timer(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Delete timer

    :param _: Parent
    :param info: Context
    :param id: Timer ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        timer = application.timers.read(UUID(id))
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    try:
        application.timers.delete(timer)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("createWatchfolder")
def resolve_create_watchfolder(
    _,
    info: GraphQLResolveInfo,
    path: str,
    re_files: Optional[str] = None,
    re_dirs: Optional[str] = None,
    added_workflow: Optional[dict] = None,
    added_variables: Optional[dict] = None,
    modified_workflow: Optional[dict] = None,
    modified_variables: Optional[dict] = None,
    deleted_workflow: Optional[dict] = None,
    deleted_variables: Optional[dict] = None,
    added_items_key: str = "watchfolder",
    modified_items_key: str = "watchfolder",
    deleted_items_key: str = "watchfolder",
):
    """
    Create watchfolder

    :param _: Parent
    :param info: Context
    :param path: Path of the folder to watch
    :param re_files: Regular expression to filter files to watch (default=None)
    :param re_dirs: Regular expression to filter directories to watch (default=None)
    :param added_workflow: Workflow instance to start when a file is added (default=None)
    :param added_variables: Initial variables for added_workflow (default=None)
    :param modified_workflow: Workflow instance to start when a file is modified (default=None)
    :param modified_variables: Initial variables for modified_workflow (default=None)
    :param deleted_workflow: Workflow instance to start when a file is deleted (default=None)
    :param deleted_variables: Initial variables for deleted_workflow (default=None)
    :param added_items_key: Key to store added files list in workflow initial variables (default="watchfolder)
    :param modified_items_key: Key to store modified files list in workflow initial variables (default="watchfolder)
    :param deleted_items_key: Key to store deleted files list in workflow initial variables (default="watchfolder)
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    added_workflow_object = None
    modified_workflow_object = None
    deleted_workflow_object = None
    if added_workflow is not None:
        try:
            added_workflow_object = application.workflows.read(
                added_workflow["id"],
                None if "version" not in added_workflow else added_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    if modified_workflow is not None:
        try:
            modified_workflow_object = application.workflows.read(
                modified_workflow["id"],
                None
                if "version" not in modified_workflow
                else modified_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    if deleted_workflow is not None:
        try:
            deleted_workflow_object = application.workflows.read(
                deleted_workflow["id"],
                None
                if "version" not in deleted_workflow
                else deleted_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    try:
        watchfolder = application.watchfolders.create(
            path,
            re_files,
            re_dirs,
            added_workflow_object,
            added_variables,
            modified_workflow_object,
            modified_variables,
            deleted_workflow_object,
            deleted_variables,
            added_items_key,
            modified_items_key,
            deleted_items_key,
        )
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True, "watchfolder": watchfolder}


@mutation.field("updateWatchfolder")
def resolve_update_watchfolder(
    _,
    info: GraphQLResolveInfo,
    id: str,  # pylint: disable=redefined-builtin
    path: str,
    re_files: Optional[str] = None,
    re_dirs: Optional[str] = None,
    added_workflow: Optional[dict] = None,
    added_variables: Optional[dict] = None,
    modified_workflow: Optional[dict] = None,
    modified_variables: Optional[dict] = None,
    deleted_workflow: Optional[dict] = None,
    deleted_variables: Optional[dict] = None,
    added_items_key: str = "watchfolder",
    modified_items_key: str = "watchfolder",
    deleted_items_key: str = "watchfolder",
):
    """
    Create watchfolder

    :param _: Parent
    :param info: Context
    :param id: Watchfolder ID
    :param path: Path of the folder to watch
    :param re_files: Regular expression to filter files to watch (default=None)
    :param re_dirs: Regular expression to filter directories to watch (default=None)
    :param added_workflow: Workflow instance to start when a file is added (default=None)
    :param added_variables: Initial variables for added_workflow (default=None)
    :param modified_workflow: Workflow instance to start when a file is modified (default=None)
    :param modified_variables: Initial variables for modified_workflow (default=None)
    :param deleted_workflow: Workflow instance to start when a file is deleted (default=None)
    :param deleted_variables: Initial variables for deleted_workflow (default=None)
    :param added_items_key: Key to store added files list in workflow initial variables (default="watchfolder)
    :param modified_items_key: Key to store modified files list in workflow initial variables (default="watchfolder)
    :param deleted_items_key: Key to store deleted files list in workflow initial variables (default="watchfolder)
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    try:
        watchfolder = application.watchfolders.read(UUID(id))
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    added_workflow_object = None
    modified_workflow_object = None
    deleted_workflow_object = None

    if added_workflow is not None:
        try:
            added_workflow_object = application.workflows.read(
                added_workflow["id"],
                None if "version" not in added_workflow else added_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    if modified_workflow is not None:
        try:
            modified_workflow_object = application.workflows.read(
                modified_workflow["id"],
                None
                if "version" not in modified_workflow
                else modified_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    if deleted_workflow is not None:
        try:
            deleted_workflow_object = application.workflows.read(
                deleted_workflow["id"],
                None
                if "version" not in deleted_workflow
                else deleted_workflow["version"],
            )
        except Exception as exception:
            return {"status": False, "error": str(exception)}

    try:
        application.watchfolders.update(
            watchfolder,
            path=path,
            re_files=re_files,
            re_dirs=re_dirs,
            added_workflow=added_workflow_object,
            added_variables=added_variables,
            modified_workflow=modified_workflow_object,
            modified_variables=modified_variables,
            deleted_workflow=deleted_workflow_object,
            deleted_variables=deleted_variables,
            added_items_key=added_items_key,
            modified_items_key=modified_items_key,
            deleted_items_key=deleted_items_key,
        )
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True, "watchfolder": watchfolder}


@mutation.field("startWatchfolder")
def resolve_start_watchfolder(
    _,
    info: GraphQLResolveInfo,
    id: str,
):  # pylint: disable=redefined-builtin
    """
    Start watchfolder ID

    :param _: Parent
    :param info: Context
    :param id: Watchfolder ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        watchfolder = application.watchfolders.read(UUID(id))
        application.watchfolders.start(watchfolder)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("stopWatchfolder")
def resolve_stop_watchfolder(
    _,
    info: GraphQLResolveInfo,
    id: str,
):  # pylint: disable=redefined-builtin
    """
    Stop watchfolder ID

    :param _: Parent
    :param info: Context
    :param id: Watchfolder ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        application.watchfolders.stop(UUID(id))
    except Exception as exception:
        print(exception)
        return {"status": False, "error": str(exception)}

    return {"status": True}


@mutation.field("deleteWatchfolder")
def resolve_delete_watchfolder(
    _,
    info: GraphQLResolveInfo,
    id: str,
):  # pylint: disable=redefined-builtin
    """
    Delete watchfolder ID

    :param _: Parent
    :param info: Context
    :param id: Watchfolder ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        watchfolder = application.watchfolders.read(UUID(id))
        application.watchfolders.delete(watchfolder)
    except Exception as exception:
        return {"status": False, "error": str(exception)}

    return {"status": True}
