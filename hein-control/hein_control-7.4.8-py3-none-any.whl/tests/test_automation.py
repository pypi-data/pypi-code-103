"""
Tests automation sequences
"""
import logging
import time
import unittest
import random

from hein_control import ConfiguredAction, EvalAction, ConfiguredDecision, Automation
from hein_control.sequencing import ConfiguredAutomation


def wait_long():
    time.sleep(0.05)
    logging.info('done waiting')


def greater_than_5(number) -> bool:
    if number > 5:
        return True
    else:
        return False


class VariableTracker:
    def __init__(self):
        self.hello_world = ''


class TestAutomationSequencing(unittest.TestCase):

    def test_basic_automation(self):  # executing in real time
        """tests basic automation"""
        action_1 = ConfiguredAction(wait_long)
        action_2 = ConfiguredAction(wait_long)
        action_1.next_action = action_2
        config_auto = ConfiguredAutomation(first_action=action_1)
        automation = config_auto.get_tracked_from_config()
        automation()
        self.assertTrue(automation.in_progress)
        self.assertFalse(automation.complete)
        time.sleep(0.05)
        self.assertTrue(automation.in_progress)
        self.assertFalse(automation.complete)
        time.sleep(0.07)
        self.assertFalse(automation.in_progress)
        self.assertTrue(automation.complete)
        for ta in automation.executed_actions:
            self.assertTrue(ta.started)
            self.assertFalse(ta.error)
            self.assertEqual(ta.status_code, 3)


class TestTurbidityEx(unittest.TestCase):
    """tests automation with a turbidity example"""

    # functions for a workflow for a turbidity experiment using log statements
    @staticmethod
    @ConfiguredAction
    def set_up_camera_config(**kwargs):
        time.sleep(0.01)
        logging.info('set up camera, start experiment')

    @staticmethod
    @ConfiguredAction
    def measure_turbidity(n_photos: int, **kwargs):  # pass in the number of photos to take
        def take_n_photos(n_photos: int):
            logging.info(f'take {n_photos} photos')
            return [i for i in range(n_photos)]

        def analyze_image(img,):
            logging.info(f'analyzing image {img}')

        imgs = take_n_photos(n_photos=n_photos)
        logging.info('analyzing a batch of images')
        for i in imgs:
            analyze_image(i)

    @staticmethod
    def is_dissolved(**kwargs) -> bool:
        choice = random.choice([True, False])
        return choice

    @staticmethod
    def is_turbid(**kwargs) -> bool:
        # for the decision action, there needs to be the case where if is_dissolved returns False,
        # there needs to be another logic check (this one) that will return true
        return True

    @staticmethod
    @ConfiguredAction
    def alert_dissolved_config(**kwargs):
        logging.info('yay, everything has dissolved')

    @staticmethod
    @ConfiguredAction
    def end_experiment_config(**kwargs):
        logging.info('end experiment')

    def test_turbidity_automation(self):  # creating and running a turbidity experiment
        """tests an automation example based on turbidity analysis"""
        # create decision action to check if an experiment should continue based on turbidity or not
        is_dissolved = ConfiguredAction(EvalAction(self.is_dissolved), next_action=self.alert_dissolved_config)
        is_turbid = ConfiguredAction(EvalAction(self.is_turbid), next_action=self.measure_turbidity)
        check_turbidity_config = ConfiguredDecision(is_dissolved, is_turbid)

        # set up next actions for the configured action functions
        self.set_up_camera_config.next_action = self.measure_turbidity  # set up camera the measure turbidity
        self.measure_turbidity.next_action = check_turbidity_config  # after measuring turbidity, check if things
        # have dissolved or not
        self.alert_dissolved_config.next_action = self.end_experiment_config  # after alerting the user, end the
        # experiment

        n_photos = 2
        turbidity_exp = ConfiguredAutomation(first_action=self.set_up_camera_config)
        self.assertEqual(self.set_up_camera_config,
                         turbidity_exp.first_action)
        # first replicate, passing in kwargs when calling the automation
        logging.info('first replicate')
        replicate_1 = turbidity_exp.get_tracked_from_config()
        self.assertEqual(None,
                         replicate_1.executed_actions)
        self.assertFalse(replicate_1.triggered)
        self.assertEqual({},
                         replicate_1.kwargs)
        replicate_1(**{'measure_turbidity': {'n_photos': n_photos}})
        replicate_1.wait_for_completion()
        self.assertTrue(replicate_1.triggered)
        self.assertFalse(replicate_1.error)
        tracked_action_list_1 = replicate_1.executed_actions
        logging.info(tracked_action_list_1)
        self.assertNotEqual(None,
                            tracked_action_list_1)
        self.assertNotEqual(0,
                            len(tracked_action_list_1))
        replicate_1_action_errors = [a.error for a in tracked_action_list_1]
        self.assertEqual(0,
                         replicate_1_action_errors.count(True))

        # second replicate, passing in kwargs when creating the tracked config
        n_photos = 10
        logging.info('second replicate')
        replicate_2 = turbidity_exp.get_tracked_from_config(**{'measure_turbidity': {'n_photos': n_photos}})
        self.assertEqual(None,
                         replicate_2.executed_actions)
        self.assertFalse(replicate_2.triggered)
        self.assertFalse(replicate_2.error)
        replicate_2()
        replicate_2.wait_for_completion()
        self.assertFalse(replicate_2.error)
        tracked_action_list_2 = replicate_2.executed_actions
        logging.info(tracked_action_list_2)
        self.assertTrue(replicate_2.triggered)
        self.assertNotEqual(None,
                            tracked_action_list_2)
        self.assertNotEqual(0,
                            len(replicate_2.executed_actions))
        replicate_2_action_errors = [a.error for a in tracked_action_list_2]
        self.assertEqual(0,
                         replicate_2_action_errors.count(True))

        # dont pass in any kwargs, should cause an error
        replicate_3 = turbidity_exp.get_tracked_from_config()
        self.assertEqual(None,
                         replicate_3.executed_actions)
        self.assertFalse(replicate_3.triggered)
        self.assertFalse(replicate_3.error)
        replicate_3()
        replicate_3.wait_for_completion()
        self.assertTrue(replicate_3.error)

