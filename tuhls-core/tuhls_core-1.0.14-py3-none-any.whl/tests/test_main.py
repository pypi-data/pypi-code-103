import json

from django.http import QueryDict
from django.test import TestCase


class QueryDictPersistanceTest(TestCase):
    def test_qd(self):
        a_q = QueryDict("a=1&a=2&c=3")
        a_s = a_q.__getstate__()
        a_j = json.dumps(a_s)

        b = QueryDict("", mutable=True)
        b.__setstate__(json.loads(a_j))
        self.assertEqual(b["a"], "2")
        self.assertEqual(b["c"], "3")
