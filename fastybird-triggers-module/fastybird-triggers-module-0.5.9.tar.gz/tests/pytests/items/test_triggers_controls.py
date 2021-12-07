#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import uuid
from kink import inject

# Library libs
from triggers_module.items import TriggerControlItem
from triggers_module.repositories import TriggersControlsRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestTriggerControlItem(DbTestCase):
    @inject
    def test_transform_to_dict(self, control_repository: TriggersControlsRepository) -> None:
        control_repository.initialize()

        control_item = control_repository.get_by_id(
            uuid.UUID("177d6fc7-1905-4fd9-b847-e2da8189dd6a", version=4)
        )

        self.assertIsInstance(control_item, TriggerControlItem)

        self.assertEqual({
            "id": "177d6fc7-1905-4fd9-b847-e2da8189dd6a",
            "name": "trigger",
            "trigger": "c64ba1c4-0eda-4cab-87a0-4d634f7b67f4",
        }, control_item.to_dict())
