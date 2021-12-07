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
from pony.orm import core as orm
from unittest.mock import patch
from exchange_plugin.publisher import Publisher

# Library libs
from triggers_module.items import ManualTriggerItem
from triggers_module.models import ManualTriggerEntity
from triggers_module.repositories import TriggersRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestManualTriggerEntity(DbTestCase):

    @inject
    def test_create_entity(self, trigger_repository: TriggersRepository) -> None:
        trigger_item = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsNone(trigger_item)

        with patch.object(Publisher, "publish") as MockPublisher:
            trigger_entity = self.__create_entity()

        MockPublisher.assert_called_once()

        self.assertIsInstance(trigger_entity, ManualTriggerEntity)
        self.assertEqual("26d7a945-ba29-471e-9e3c-304ef0acb199", trigger_entity.trigger_id.__str__())
        self.assertEqual("New manual trigger name", trigger_entity.name)
        self.assertTrue(trigger_entity.enabled)
        self.assertIsNotNone(trigger_entity.created_at)

        trigger_item = trigger_repository.get_by_id(
            trigger_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
        )

        self.assertIsInstance(trigger_item, ManualTriggerItem)

    # -----------------------------------------------------------------------------

    @staticmethod
    @orm.db_session
    def __create_entity() -> ManualTriggerEntity:
        trigger_entity = ManualTriggerEntity(
            trigger_id=uuid.UUID("26d7a945-ba29-471e-9e3c-304ef0acb199", version=4),
            name="New manual trigger name",
        )

        return trigger_entity
