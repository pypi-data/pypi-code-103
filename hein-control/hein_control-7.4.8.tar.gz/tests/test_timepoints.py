import time
import unittest
from hein_control.timepoint import TimePoint, ActionTimePoint

tp_name = f'test 1'
tp_desc = 'test case time point'

one_second_return = 'abcde'
fifty_return = [1, 2, 3, 4, 5]


def one_second():
    time.sleep(1)
    return one_second_return


def fifty_ms():
    time.sleep(0.05)
    return fifty_return


class TestTimePoint(unittest.TestCase):
    def setUp(self) -> None:
        self.tp_one = TimePoint(
            1.,
            name=tp_name,
            description=tp_desc
        )

    def test_class(self):
        """tests basic functionality of the class"""
        self.assertEqual(
            self.tp_one.name,
            tp_name
        )
        self.assertEqual(
            1.,
            self.tp_one.time_delta,
        )
        self.assertEqual(
            tp_desc,
            self.tp_one.description
        )

    def test_instance_retrieval(self):
        """tests instance retrieval method"""
        self.assertTrue(
            self.tp_one is TimePoint.class_instance_by_id(self.tp_one._uuid)
        )
        self.assertTrue(
            self.tp_one is TimePoint.class_instance_by_id(self.tp_one.uuid)
        )

    def test_magic_methods(self):
        """tests comparison methods"""
        self.assertTrue(
            self.tp_one < TimePoint(2)
        )
        self.assertTrue(
            self.tp_one <= TimePoint(2)
        )
        self.assertTrue(
            self.tp_one > TimePoint(0.5)
        )
        self.assertTrue(
            self.tp_one >= TimePoint(0.5)
        )
        self.assertTrue(
            self.tp_one == TimePoint(1)
        )


class TestActionTimePoint(unittest.TestCase):
    def test_sequencing(self):
        atp = ActionTimePoint.create_from_actions(
            3.,
            actions=[fifty_ms]
        )
        atp.trigger()
        atp.wait_for_completion()
        self.assertRaises(
            SystemError,
            atp.trigger,
        )

        # todo better test for these retrievals
        durations = atp.action_durations
        starts = atp.action_start_times
        ends = atp.action_completion_times
        action_returns = atp.action_returns
        timestamps = atp.started_timestamps
        dct = atp.as_dict()

    def test_flags(self):
        atp = ActionTimePoint.create_from_actions(
            3,
            actions=[one_second]
        )
        atp.trigger()
        self.assertTrue(
            atp.in_progress
        )
        self.assertFalse(
            atp.complete
        )
        atp.wait_for_completion()
        self.assertFalse(atp.in_progress)
        self.assertTrue(atp.complete)
