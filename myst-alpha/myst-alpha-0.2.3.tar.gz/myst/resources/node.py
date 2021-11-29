from typing import Optional
from uuid import UUID

from myst.openapi.models.deploy_status import DeployStatus
from myst.resources.resource import ShareableResource


class Node(ShareableResource):
    """A node in a project graph.

    Attributes:
        project: identifier of the project to which this node belongs
        title: the title of this node
        description: a brief description of the node
        deploy_status: whether this node is new, deployed, or inactive
    """

    project: UUID
    title: str
    description: Optional[str] = None
    deploy_status: DeployStatus
