# SPDX-FileCopyrightText: Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import json
from uuid import UUID


class SQLAlchemyJSONEncoder(json.JSONEncoder):
    """Extends the basic JSON encoder for JSONB fields, among others

    Extends the basic JSON encoder and serializes certain objects to JSON in
    a format we understand. For now the following objects get encoded:

    * UUID

    Examples:

        UUID('18c0004e-5c7c-4836-abab-0c0ec4cdeea0') to '18c0004e-5c7c-4836-abab-0c0ec4cdeea0'

    """

    def default(self, obj):
        # Only added support for UUID right now
        if isinstance(obj, UUID):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def _json_encoder(structure):
    return json.dumps(structure, cls=SQLAlchemyJSONEncoder)
