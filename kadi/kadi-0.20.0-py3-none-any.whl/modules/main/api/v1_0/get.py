# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_response
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import normalize
from kadi.lib.licenses.schemas import LicenseSchema
from kadi.lib.tags.schemas import TagSchema
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.lib.web import url_for
from kadi.modules.main.utils import get_licenses as _get_licenses
from kadi.modules.main.utils import get_tags as _get_tags
from kadi.modules.permissions.utils import get_object_roles
from kadi.version import __version__


@bp.get("")
@login_required
@status(200, "Return the API endpoints.")
def index():
    """Get all base API endpoints."""
    endpoints = {
        "collections": url_for("api.get_collections"),
        "groups": url_for("api.get_groups"),
        "info": url_for("api.get_info"),
        "licenses": url_for("api.get_licenses"),
        "records": url_for("api.get_records"),
        "roles": url_for("api.get_resource_roles"),
        "tags": url_for("api.get_tags"),
        "templates": url_for("api.get_templates"),
        "trash": url_for("api.get_trash"),
        "users": url_for("api.get_users"),
    }
    return json_response(200, endpoints)


@bp.get("/info")
@login_required
@status(200, "Return the information about the Kadi instance.")
def get_info():
    """Get information about the Kadi instance."""
    info = {"version": __version__}
    return json_response(200, info)


@bp.get("/roles")
@login_required
@status(200, "Return the resource roles and permissions.")
def get_resource_roles():
    """Get all possible roles and corresponding permissions of all resources."""
    roles = {}

    for object_name in ["record", "collection", "group", "template"]:
        roles[object_name] = get_object_roles(object_name)

    return json_response(200, roles)


@bp.get("/tags")
@login_required
@paginated
@qparam(
    "filter", parse=normalize, description="A query to filter the tags by their name."
)
@qparam(
    "type",
    default=None,
    description="A resource type to limit the tags to. One of ``record`` or"
    " ``collection``.",
)
@status(200, "Return a paginated list of tags, sorted by name in ascending order.")
def get_tags(page, per_page, qparams):
    """Get all tags."""
    paginated_tags = _get_tags(
        filter_term=qparams["filter"], resource_type=qparams["type"]
    ).paginate(page, per_page, False)

    data = {
        "items": TagSchema(many=True).dump(paginated_tags.items),
        **create_pagination_data(
            paginated_tags.total, page, per_page, "api.get_tags", **qparams
        ),
    }

    return json_response(200, data)


@bp.get("/licenses")
@login_required
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the licenses by their title or name.",
)
@status(200, "Return a paginated list of licenses, sorted by name in ascending order.")
def get_licenses(page, per_page, qparams):
    """Get all licenses."""
    paginated_licenses = _get_licenses(filter_term=qparams["filter"]).paginate(
        page, per_page, False
    )

    data = {
        "items": LicenseSchema(many=True).dump(paginated_licenses.items),
        **create_pagination_data(
            paginated_licenses.total, page, per_page, "api.get_licenses", **qparams
        ),
    }

    return json_response(200, data)
