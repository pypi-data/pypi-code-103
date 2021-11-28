import json
import sys
from pprint import pprint

import pytest

from superwise import Superwise
from superwise.controller.exceptions import *
from superwise.models.task import Task
from tests import config
from tests import get_sw
from tests import print_results


@pytest.mark.vcr()
def test_task_type_roles():
    ## FIXME - for gui bring back later
    return
    sw = get_sw()
    model = sw.role.get_by_task_type_id(1)
    for m in model:
        print(m.get_properties())
    assert len(model) == 9
