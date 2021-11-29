import json
from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from myst.client import get_client
from myst.core.time.time import Time
from myst.openapi.api.models import get_model_fit_result
from myst.resources.resource import Resource


class NodeResult(Resource):
    """Describes a result associated with a node.

    Attributes:
        node: the UUID of the node this result corresponds to
        start_time: the start time of this result
        end_time: the end time of this result
        as_of_time: the as of time of this result
    """

    node: UUID
    start_time: Time
    end_time: Time
    as_of_time: Time


class ModelFitResult(NodeResult):
    """Results from a single run of a model fit.

    Attributes:
        fit_state_url: an external URL to the model fit state blob
    """

    fit_state_url: Optional[str]

    def download_fit_state(self) -> Dict[str, Any]:
        """Downloads the fit state from the supplied URL and parses it."""
        # Lazy load the fit state URL, for example if this object was acquired through a list rather than a get.
        if self.fit_state_url is None:
            model_fit_result_detailed = get_model_fit_result.request_sync(
                client=get_client(), model_uuid=str(self.node), uuid=str(self.uuid)
            )
            self.fit_state_url = model_fit_result_detailed.fit_state_url

        response = httpx.get(self.fit_state_url)

        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise RuntimeError("Could not download fit state.")
