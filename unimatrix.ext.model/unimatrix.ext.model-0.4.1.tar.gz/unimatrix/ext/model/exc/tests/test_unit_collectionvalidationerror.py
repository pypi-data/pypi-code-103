# pylint: skip-file
import unittest

from .. import ValidationError
from .. import CollectionValidationError
from ..schema import CanonicalExceptionSchema


class CollectionValidationErrorTestCase(unittest.TestCase):

    def test_create_from_marshmallow_exception(self):
        schema = CanonicalExceptionSchema()
        try:
            schema.load({})
        except Exception as e:
            items = [
                ValidationError(spec=e.normalized_messages(), index=2),
                ValidationError(spec=e.normalized_messages(), index=4)
            ]
            exc = CollectionValidationError(items=items)
            dto = exc.as_dict()
            self.assertIn('items', dto)
            self.assertEqual(dto['items'][0]['index'], 2)
            self.assertEqual(dto['items'][1]['index'], 4)
        else:
            self.fail()
