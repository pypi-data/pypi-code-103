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

from typing import List, Optional
from uuid import UUID

from ariadne import InterfaceType, QueryType
from graphql.type.definition import GraphQLResolveInfo

from madam.domains.application import MainApplication
from madam.domains.entities.agent import Agent
from madam.domains.entities.application import Application
from madam.domains.entities.job import Job
from madam.domains.entities.timer import Timer
from madam.domains.entities.watchfolder import Watchfolder
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import WorkflowInstance

query = QueryType()

timer_interface = InterfaceType("Timer")


@timer_interface.type_resolver
def resolve_timer_interface_type(obj, *_):
    """
    Return type of object as string for this interface

    :param obj: Instance to resolve
    :param _: Unused
    :return:
    """
    if hasattr(obj, "repeat"):
        return "CyclicTimer"

    if hasattr(obj, "date"):
        return "DateTimer"

    return None


@query.field("version")
def resolve_version(_, info: GraphQLResolveInfo):
    """
    Get Madam version

    :param _: Parent
    :param info: Context
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    return application.get_version()


@query.field("agents")
def resolve_agents(_, info: GraphQLResolveInfo):
    """
    Get Madam agents list

    :param _: Parent
    :param info: Context
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    if info.field_nodes[0].selection_set is not None:
        fields_selection = info.field_nodes[0].selection_set.selections

        if len(fields_selection) == 1:
            field = fields_selection[
                0
            ]  # mypy see SelectionNode, but real type is FieldNode
            if field.name.value == "name":  # type: ignore
                names = application.agents.list(only_names=True)
                return [{"name": name} for name in names]

    agents = application.agents.list()
    agents_serialized: List[dict] = []
    for agent in agents:
        if isinstance(agent, Agent):
            agents_serialized.append(_agent_serializer(agent))

    return agents_serialized


@query.field("agent")
def resolve_agent(_, info: GraphQLResolveInfo, name: str):
    """
    Get Madam agent documentation

    :param _: Parent
    :param info: Context
    :param name: Agent's name
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        agent = application.agents.read(name)
    except ModuleNotFoundError:
        return None

    return None if agent is None else _agent_serializer(agent)


def _agent_serializer(agent: Agent) -> dict:
    """
    Serialize Agent instance to dict
    (required to deliver AgentApplication GraphQL type)

    :param agent: Agent instance
    :return:
    """
    # serialize applications to AgentApplication
    agent_applications: Optional[List[dict]] = None
    if agent.applications is not None:
        agent_applications = []
        for application_label, agent_application in agent.applications.items():
            agent_applications.append(
                {
                    "label": application_label,
                    "name": agent_application.name,
                    "version": agent_application.version,
                }
            )

    return {"name": agent.name, "help": agent.help, "applications": agent_applications}


@query.field("workflow")
def resolve_workflow(
    _, info: GraphQLResolveInfo, id: str, version: Optional[int]
):  # pylint: disable=redefined-builtin
    """
    Get workflow from ID and version

    :param _: Parent
    :param info: Context
    :param id: Workflow ID
    :param version: Workflow version
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        workflow = application.workflows.read(id, version)
    except Exception:
        return None

    return workflow


@query.field("workflows")
def resolve_workflows_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    last_version: bool,
):
    """
    Get a Workflows object from workflows.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param last_version: Return only last version if True
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[Workflow] = []

    try:
        count = application.workflows.count(last_version)
    except Exception:
        return {"count": 0, "result": result}

    try:
        workflows = application.workflows.list(
            offset, limit, sort_column, sort_ascending, last_version
        )
    except Exception:
        return {"count": 0, "result": result}

    for workflow in workflows:
        result.append(workflow)

    return {"count": count, "result": result}


@query.field("workflow_instance")
def resolve_workflow_instance(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Get workflow instance from ID

    :param _: Parent
    :param info: Context
    :param id: Workflow instance ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        instance = application.workflow_instances.read(UUID(id))
    except Exception:
        return None

    return instance


@query.field("workflow_instances")
def resolve_workflow_instances_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    status: Optional[str],
    workflow: Optional[dict],
):
    """
    Get an Instances object from workflow_instances.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param status: Instance status filter
    :param workflow: Parent Workflow filter as WorkflowInput {"id": str, ["version": Optional[int]]}
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[WorkflowInstance] = []

    version = (
        workflow["version"] if workflow is not None and "version" in workflow else None
    )
    workflow_ = None

    if workflow is not None:
        try:
            workflow_ = application.workflows.read(workflow["id"], version)
        except Exception:
            return {"count": 0, "result": result}

    try:
        count = application.workflow_instances.count(status, workflow_)
    except Exception:
        return {"count": 0, "result": result}

    try:
        instances = application.workflow_instances.list(
            offset, limit, sort_column, sort_ascending, status, workflow_
        )
    except Exception:
        return {"count": 0, "result": result}

    for instance in instances:
        result.append(instance)

    return {"count": count, "result": result}


@query.field("timer")
def resolve_timer(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Get Timer from ID

    :param _: Parent
    :param info: Context
    :param id: Timer ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        timer = application.timers.read(UUID(id))
    except Exception:
        return None

    return timer


@query.field("timers")
def resolve_timers_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    status: Optional[str],
    workflow: Optional[dict],
):
    """
    Get a Timers object from timers.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param status: Instance status filter
    :param workflow: Parent Workflow filter as WorkflowInput {"id": str, ["version": Optional[int]]}
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[Timer] = []

    version = (
        workflow["version"] if workflow is not None and "version" in workflow else None
    )
    workflow_ = None

    if workflow is not None:
        try:
            workflow_ = application.workflows.read(workflow["id"], version)
        except Exception:
            return {"count": 0, "result": result}

    try:
        count = application.timers.count(status, workflow_)
    except Exception:
        return {"count": 0, "result": result}

    try:
        timers = application.timers.list(
            offset, limit, sort_column, sort_ascending, status, workflow_
        )
    except Exception:
        return {"count": 0, "result": result}

    for timer in timers:
        result.append(timer)

    return {"count": count, "result": result}


@query.field("job")
def resolve_job(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Get Job from ID

    :param _: Parent
    :param info: Context
    :param id: Job ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        job = application.jobs.read(UUID(id))
    except Exception:
        return None

    return job


@query.field("jobs")
def resolve_jobs_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    status: Optional[str],
    workflow_instance_id: Optional[str],
):
    """
    Get a Jobs object from jobs.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param status: Instance status filter
    :param workflow_instance_id: Parent WorkflowInstance ID filter
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[Job] = []
    workflow_instance_uuid = (
        UUID(workflow_instance_id) if workflow_instance_id is not None else None
    )

    try:
        count = application.jobs.count(status, workflow_instance_uuid)
    except Exception:
        return {"count": 0, "result": result}

    try:
        jobs = application.jobs.list(
            offset, limit, sort_column, sort_ascending, status, workflow_instance_uuid
        )
    except Exception:
        return {"count": 0, "result": result}

    for job in jobs:
        result.append(job)

    return {"count": count, "result": result}


@query.field("application")
def resolve_application(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Get Application from ID

    :param _: Parent
    :param info: Context
    :param id: Application ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        application_ = application.applications.read(UUID(id))
    except Exception:
        return None

    return application_


@query.field("applications")
def resolve_applications_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    status: Optional[str],
    job_id: Optional[str],
):
    """
    Get an Applications object from applications.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param status: Instance status filter
    :param job_id: Parent Job ID filter
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[Application] = []
    job_uuid = UUID(job_id) if job_id is not None else None

    try:
        count = application.applications.count(status, job_uuid)
    except Exception:
        return {"count": 0, "result": result}

    try:
        applications = application.applications.list(
            offset, limit, sort_column, sort_ascending, status, job_uuid
        )
    except Exception:
        return {"count": 0, "result": result}

    for application_ in applications:
        result.append(application_)

    return {"count": count, "result": result}


@query.field("watchfolder")
def resolve_watchfolder(
    _, info: GraphQLResolveInfo, id: str
):  # pylint: disable=redefined-builtin
    """
    Get workflow from ID and version

    :param _: Parent
    :param info: Context
    :param id: Watchfolder ID
    :return:
    """
    application = info.context["application"]  # type: MainApplication

    try:
        watchfolder = application.watchfolders.read(UUID(id))
    except Exception:
        return None

    return watchfolder


@query.field("watchfolders")
def resolve_watchfolders_list(
    _,
    info: GraphQLResolveInfo,
    offset: int,
    limit: int,
    sort_column: str,
    sort_ascending: bool,
    status: Optional[str],
    workflow: Optional[dict],
):
    """
    Get an Instances object from workflow_instances.list

    :param _: Parent type
    :param info: GraphQLResolveInfo instance
    :param offset: Offset in result
    :param limit: Max number of elements in result
    :param sort_column: Column to order by
    :param sort_ascending: Order by ascending if True
    :param status: Watchfolder status filter
    :param workflow: Triggered Workflow filter as WorkflowInput {"id": str, ["version": Optional[int]]}
    :return:
    """
    application = info.context["application"]  # type: MainApplication
    result: List[Watchfolder] = []

    version = (
        workflow["version"] if workflow is not None and "version" in workflow else None
    )
    workflow_ = None

    if workflow is not None:
        try:
            workflow_ = application.workflows.read(workflow["id"], version)
        except Exception:
            return {"count": 0, "result": result}

    try:
        count = application.watchfolders.count(status, workflow_)
    except Exception:
        return {"count": 0, "result": result}

    try:
        watchfolders = application.watchfolders.list(
            offset, limit, sort_column, sort_ascending, status, workflow_
        )
    except Exception:
        return {"count": 0, "result": result}

    for watchfolder in watchfolders:
        result.append(watchfolder)

    return {"count": count, "result": result}
