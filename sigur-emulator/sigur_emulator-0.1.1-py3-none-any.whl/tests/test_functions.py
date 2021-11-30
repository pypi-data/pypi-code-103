from sigure_emulator import functions
from sigure_emulator import responses
import unittest
import datetime


class FunctionsTest(unittest.TestCase):

    def test_get_point_dict(self):
        response = functions.create_points_dict(4)
        self.assertTrue(len(response) == 4)

    def test_emulate_event_ce_rfid(self):
        rfid_number = 'FFFF000123'
        timestamp = datetime.datetime.now()
        response = functions.get_emulated_event_ce_rfid_read(1, rfid_number, timestamp=timestamp)
        response_must = responses.event_ce_rfid_read_response_mask.format(timestamp, 1, "W42", rfid_number)
        self.assertEqual(response, response_must)

    def test_emulate_event_ce_status(self):
        timestamp = datetime.datetime.now()
        response_must = 'EVENT_CE "{}" 31 1 0 0 UNKNOWN\r\n'.format(timestamp)
        response = functions.get_emulated_event_ce_point_changed(1, 31, timestamp=timestamp)
        self.assertEqual(response, response_must)

    def test_emulate_lock_status(self):
        timestamp = datetime.datetime.now()
        response_must = 'EVENT_CE "{}" 31 1 0 0 UNKNOWN\r\n'.format(timestamp)
        response = functions.get_emulated_locked_event(1, timestamp=timestamp)
        self.assertEqual(response, response_must)

    def test_emulate_unlock_status(self):
        timestamp = datetime.datetime.now()
        response_must = 'EVENT_CE "{}" 32 1 0 0 UNKNOWN\r\n'.format(timestamp)
        response = functions.get_emulated_unlocked_event(1, timestamp=timestamp)
        self.assertEqual(response, response_must)

    def test_emulate_normal_status(self):
        timestamp = datetime.datetime.now()
        response_must = 'EVENT_CE "{}" 30 1 0 0 UNKNOWN\r\n'.format(timestamp)
        response = functions.get_emulated_normal_event(1, timestamp=timestamp)
        self.assertEqual(response, response_must)

if __name__ == "__main__":
    unittest.main()