"""
Tests ordered sequencing utilities for
"""

import time
import unittest
import logging

from hein_control.action import (Action, ConfiguredAction, ActionList,
                                 ConfiguredActionList, TrackedActionList, TrackedAction)
from hein_control.sequencing import ExecutionSequence, ConfiguredSequence
from hein_control.mixin import is_jsonable

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def first():
    logging.info('first')
    time.sleep(0.1)


def second():
    logging.info('second')
    time.sleep(0.2)


def third():
    logging.info('third')
    time.sleep(0.3)


def error():
    raise ValueError('something has gone horrible wrong! (intentionally)')


def as_dict_serializable(action) -> bool:
    """verifies that the as_dict representation is serializable"""
    return is_jsonable(action.as_dict())


class TestLists(unittest.TestCase):
    def test_action_list(self):
        """tests the ActionList class"""
        reg_second = Action.register_action(second)
        al = ActionList(first, reg_second, third)
        self.assertTrue(all([
            isinstance(action, Action) for action in al
        ]))
        ca = ConfiguredAction(first)
        al.append(ca)
        self.assertTrue(isinstance(al[-1], Action))

    def test_configaction_list(self):
        """tests the ConfiguredActionList class"""
        cal = ConfiguredActionList(first, second)
        cal.append(third)
        cal.append('second')
        self.assertTrue(all([
            isinstance(action, ConfiguredAction) for action in cal
        ]))

    def test_tr_list(self):
        """tests the TrackedActionList class"""
        tral = TrackedActionList(first, second)
        tral.append('second')
        tral.append(third)
        self.assertTrue(all([
            isinstance(action, TrackedAction) for action in tral
        ]))


class TestExecSequence(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # create configured actions
        cls.c_first = ConfiguredAction(first)
        cls.c_second = ConfiguredAction(second)
        cls.c_third = ConfiguredAction(third)

        cls.seq = ConfiguredSequence(
            cls.c_first,
            cls.c_second,
            cls.c_third,
            sequence_name='test sequence'
        )
        cls.tracked = ExecutionSequence(cls.seq)

        cls.attrs = [
            'action_returns',
            'actions_status',
            'action_start_times',
            'action_completion_times',
            'action_durations',
            'started_timestamps',
        ]

    def test_ordering(self):
        """test action ordering"""
        # ensure configurations are mapped correctly
        for ca, orig in zip(self.seq.action_sequence, [self.c_first, self.c_second, self.c_third]):
            self.assertIs(ca, orig)

    def test_execution(self):
        """tests execution of sequences"""
        self.assertTrue(as_dict_serializable(self.tracked))
        self.tracked()
        self.assertTrue(as_dict_serializable(self.tracked))
        self.tracked.wait_for_completion()
        self.assertTrue(as_dict_serializable(self.tracked))
        for attr in self.attrs:
            self.assertIsNotNone(
                getattr(self.tracked, attr)
            )

    def test_errors(self):
        """tests attribute error raising if not executed"""
        unexec = self.tracked.copy_configuration()

        for attr in self.attrs:
            self.assertRaises(
                AttributeError,
                getattr,
                unexec,
                attr
            )

    def test_duplication(self):
        """test duplication of class instance"""
        # test duplication
        tracked_2 = self.tracked.copy_configuration()
        tracked_2()

        seq2 = self.seq.duplicate_configuration()
        self.assertFalse(seq2 is self.seq)

    def test_string_spec(self):
        """test string specification and instance retrieval"""
        spec_2 = ExecutionSequence('test sequence')
        spec_2.trigger()  # tests specific trigger method
        spec_2.wait_for_completion()

        # test retrieval by string and pass through
        spec_3 = ConfiguredSequence.class_instance_by_id('test sequence')
        spec_4 = ExecutionSequence(spec_3)

    def test_sequence_errors(self):
        """tests that errors are correctly caught in sequences"""
        seq = self.seq.duplicate_configuration()
        seq.action_sequence.append(error)  # append error function to duplicated sequence
        tracked = seq.get_tracked_from_config()  # get a tracked version
        tracked()  # execute
        tracked.wait_for_completion()
        self.assertTrue(tracked.error)  # ensure error state is propagated
        self.assertIsNotNone(tracked.error_details)
        self.assertTrue(tracked.args[-1].error)  # ensure correct function is errored
