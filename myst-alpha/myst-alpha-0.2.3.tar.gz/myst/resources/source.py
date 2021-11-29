from typing import TYPE_CHECKING, Optional

from myst.client import get_client
from myst.connectors.source_connector import SourceConnector
from myst.models.types import UUIDOrStr, to_uuid
from myst.openapi.api.sources import create_source, get_source
from myst.openapi.models.source_create import SourceCreate
from myst.resources.connector_node import ConnectorNode

if TYPE_CHECKING:  # Avoid circular imports.
    from myst.resources.project import Project


class Source(ConnectorNode):
    """A node which produces data without any inputs."""

    @classmethod
    def create(
        cls, project: "Project", title: str, connector: SourceConnector, description: Optional[str] = None
    ) -> "Source":
        """Creates a new source node.

        Args:
            project: the project in which to create the source
            title: the title of the source
            connector: the source connector to use in the source node
            description: a brief description of the source

        Returns:
            the newly created source
        """
        source = create_source.request_sync(
            client=get_client(),
            json_body=SourceCreate(
                object="Node",
                type="Source",
                title=title,
                description=description,
                project=str(project.uuid),
                connector_uuid=str(connector.uuid),
                parameters=connector.parameters_exclude_none(),
            ),
        )

        return Source.parse_obj(source.dict())

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "Source":
        """Gets a specific source by its identifier."""
        source = get_source.request_sync(client=get_client(), uuid=str(to_uuid(uuid)))

        return Source.parse_obj(source.dict())
