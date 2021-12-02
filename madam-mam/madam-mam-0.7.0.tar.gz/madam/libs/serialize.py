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

"""
Serialize module
"""
import json
import uuid
from datetime import datetime
from json import JSONDecoder, JSONEncoder

from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import WorkflowInstance


class WorkflowInstanceJSONEncoder(JSONEncoder):
    """
    WorkflowInstanceJSONEncoder class
    """

    def default(self, o):
        """
        Encode special classes

        :param o: Object to encode
        :return:
        """
        if isinstance(o, datetime):
            # iso format string for datetime
            return {"__datetime__": o.isoformat()}

        if isinstance(o, uuid.UUID):
            # string representation for UUID
            return {"__UUID__": str(o)}

        # other classes get their dict
        return {f"__{o.__class__.__name__}__": o.__dict__}


def workflow_instance_object_hook(dict_):
    """
    Decode serialized custom classes

    :param dict_: Dictionary of values
    :return:
    """
    if "__WorkflowInstance__" in dict_:
        # decode workflow instance object
        return WorkflowInstance(**dict_["__WorkflowInstance__"])

    if "__Workflow__" in dict_:
        # decode workflow object
        return Workflow(**dict_["__Workflow__"])

    if "__datetime__" in dict_:
        # decode from iso datetime string
        return datetime.fromisoformat(dict_["__datetime__"])

    if "__UUID__" in dict_:
        # decode from UUID string
        return uuid.UUID(dict_["__UUID__"])

    return dict_


class WorkflowInstanceJSONDecoder(JSONDecoder):
    """
    WorkflowInstanceJSONDecoder class
    """

    def __init__(self, *args, **kwargs):
        self.object_hook = workflow_instance_object_hook
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
