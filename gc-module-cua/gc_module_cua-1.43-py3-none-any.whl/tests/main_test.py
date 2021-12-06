from gc_module_cua.main import EventsCatcher
from gc_module_cua.tests.sqlshell_test import sql_shell
from gc_module_cua.tests import settings_test as s
import unittest


class MainTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.ec = EventsCatcher(sql_shell, s.cm_events_table, s.cm_events_log)

    def test_make_record(self):
        value = self.ec.try_capture_new_event(event='ENTER', additional='TEST')
        print(value)

