import logging
import time
import unittest
from hein_control.action import Action, EvalAction, TrackedDecision, ConfiguredAction, ConfiguredDecision, \
    ThreadedTrackedAction, TrackedAction, ConfiguredActionList, ConfigurableInstance
from hein_control.action.operators import execute_sequence_actions, run_automation, decision
from hein_control.mixin import Configuration, Status, is_jsonable

logger = logging.getLogger(__name__)

one_second_return = 'abcde'
fifty_return = [1, 2, 3, 4, 5]


def one_second():
    time.sleep(1)
    return one_second_return


def fifty_ms():
    time.sleep(0.05)
    return fifty_return


def user_time(dur, **kwargs):
    time.sleep(dur)
    return kwargs


def five_second():
    time.sleep(5.)
    return fifty_return

def return_true(*args, **kwargs) -> bool:
    return True

def return_false(*args, **kwargs) -> bool:
    return False

error_details = 'you did something horrific and it broke the code'


def erronious():
    raise ValueError(error_details)


def passthrough(*args, **kwargs):
    return args, kwargs


def as_dict_serializable(action) -> bool:
    """verifies that the as_dict representation is serializable"""
    return is_jsonable(action.as_dict())


class TestActions(unittest.TestCase):
    def setUp(self) -> None:
        # register all actions
        Action.register_action(one_second)
        Action.register_action(fifty_ms)
        Action.register_action(user_time)

    def test_registry(self):
        """tests registry functionality of SchedulerAction"""
        self.assertTrue(
            Action.action_is_registered(one_second)
        )
        self.assertTrue(
            Action.action_is_registered(fifty_ms)
        )

    def test_basic_action(self):
        """test functionality of action calling and return"""
        action = Action.register_action(one_second)
        self.assertEqual(  # test name attribute
            action.name,
            one_second.__name__
        )
        ret = action()  # execute action, test return
        self.assertEqual(
            one_second_return,
            ret
        )

    def test_argument_passthrough(self):
        """tests argument and kwarg passthrough"""
        action = Action.register_action(passthrough)
        args = (0.123, 123, 456)
        kwargs = {'asdf': 'qwerty'}
        ret = action(
            *args,
            **kwargs
        )
        self.assertEqual(
            (args, kwargs),
            ret
        )

    def test_props(self):
        """tests properties of trackedaction"""
        pass  # todo

    def test_duplication(self):
        """tests duplication of TrackedAction"""
        act = TrackedAction(passthrough)
        act2 = act.copy_configuration()
        act()
        self.assertRaises(  # verify that action cannot be executed twice
            RuntimeError,
            act,
        )
        act2()  # ... and that "copy" instance still works

    def test_threaded(self):
        """test threaded tracked action"""
        act = ThreadedTrackedAction(user_time)
        self.assertFalse(act.triggered)
        self.assertFalse(act.started)
        act(dur=0.2)
        self.assertTrue(act.triggered)
        self.assertTrue(act.in_progress)
        act.wait_for_completion()
        self.assertTrue(act.complete)

    def test_arg_kwarg(self):
        """tests argument and kwarg specification and passthrough"""
        args = (0.123, 123, 456)
        kwargs = {'asdf': 'qwerty'}
        # test argument updating
        action = TrackedAction(
            passthrough,
            *args,
            **kwargs
        )
        self.assertEqual(
            action.args,
            args
        )
        self.assertEqual(
            action.kwargs,
            kwargs
        )
        action(
            789,
            asdf='al;skdjf;'
        )
        self.assertEqual(
            action.args,
            (789, 123, 456)
        )
        self.assertEqual(
            action.kwargs,
            {'asdf': 'al;skdjf;'}
        )

    def test_next_action_kwarg(self):
        """tests passing a next action"""
        args = (0.123, 123, 456)
        kwargs = {'asdf': 'qwerty'}
        config_1 = ConfiguredAction(
            passthrough,
            *args,
            **kwargs
        )
        tracked = TrackedAction(ConfiguredAction)
        args2 = (1, 2)
        kwargs2 = {'squirrels': 'cool'}
        config_2 = ConfiguredAction(
            passthrough,
            *args2,
            **kwargs2
        )
        self.assertIsNone(
            config_1.next_action
        )
        self.assertIsNone(
            tracked.next_action
        )
        config_1.next_action = config_2
        self.assertEqual(
            config_1.next_action,
            config_2,
        )

    def test_error_catching(self):
        """tests that errors are properly raised"""
        action = Action.register_action(erronious)
        self.assertRaises(
            ValueError,
            action
        )
        self.assertRaises(
            TypeError,
            Action,
            ('asdf123'),
            'check that non-callables are correctly rejected as actions'
        )


def return_str() -> str:
    return 'metal'


def return_true() -> bool:
    return True


def return_false() -> bool:
    return False


class ConditionClass:
    flag = False


class TestConfiguredAction(unittest.TestCase):
    def test_instance_by_id(self):
        # todo docstrings suggest that only the UUID can be used
        conf_action_1 = ConfiguredAction(passthrough,
                                         configuration_name='config_test_by_id',)
        self.assertRaises(
            NameError,
            ConfiguredAction.class_instance_by_id,
            ('this_should_be_undefined'),
        )

    def test_serializable(self):
        """tests that the registered actions are serializable"""
        conf_action_apple = ConfiguredAction(passthrough,
                                             configuration_name='apple')
        self.assertTrue(as_dict_serializable(conf_action_apple))

    def test_configured_action(self):
        """test all the methods of the configured action class"""
        args = ('metal', 'squirrel')
        kwargs = {'squirrels': 'are cute'}
        conf_action_apple = ConfiguredAction(passthrough,
                                             configuration_name='apple',
                                             *args,
                                             **kwargs)
        conf_action_orange = conf_action_apple.duplicate_configuration(new_name='orange')
        self.assertEqual(
            f'0: {Status.ACTION_STATES[0]}',
            conf_action_apple.status,
        )
        self.assertEqual(conf_action_apple.name,
                         'apple')
        self.assertEqual(conf_action_orange.name,
                         'orange')

        self.assertEqual(conf_action_apple.next_action
                         , None)
        self.assertEqual(conf_action_orange.previous_actions,
                         [])

        conf_action_apple.next_action = conf_action_orange
        self.assertEqual(conf_action_apple.next_action,
                         conf_action_orange)
        self.assertEqual(conf_action_orange.previous_actions,
                         [conf_action_apple])

        self.assertEqual(ConfiguredAction.class_instance_by_id(conf_action_apple.uuid),
                         conf_action_apple)
        self.assertEqual(ConfiguredAction.search_class_for_id(conf_action_apple.uuid, 'ConfiguredAction'),
                         conf_action_apple)
        # todo throws a  TrackedAction error for some reason when running all the unit tests, but passes when only
        #  this test is run
        self.assertIs(ConfiguredAction.get_instance_by_uuid(conf_action_apple.uuid),
                      conf_action_apple)

        self.assertEqual(ConfiguredAction.ensure_configuration(conf_action_apple),
                         conf_action_apple)
        self.assertEqual(ConfiguredAction.ensure_configuration(conf_action_apple),
                         conf_action_apple)
        self.assertEqual(ConfiguredAction.ensure_configuration(conf_action_apple.name),
                         conf_action_apple)
        conf_action_pear = ConfiguredAction.ensure_configuration(passthrough)
        self.assertEqual(conf_action_pear,
                         ConfiguredAction.class_instance_by_id(conf_action_pear.uuid))
        self.assertIs(ConfiguredAction.ensure_configuration(one_second),
                      ConfiguredAction.class_instance_by_id('one_second'))
        self.assertRaises(
            ValueError,
            ConfiguredAction.ensure_configuration,
            ('not a registered action'),
        )

        tracked = conf_action_apple.get_tracked_from_config()
        self.assertEqual(conf_action_apple,
                         tracked.configuration)
        self.assertEqual(TrackedAction,
                         type(tracked))

    def test_conditional_configured_action(self):
        """tests the conditional configured action setup"""
        flag = False
        def evaluator():
            return flag

        cond = ConfiguredAction(return_str, condition=evaluator)
        track_1 = cond.get_tracked_from_config()
        track_1()
        self.assertEqual(track_1.status_code, 3)
        self.assertIsNone(track_1.action_return, "ensure that the action didn't run")
        flag = True
        track_2 = cond.get_tracked_from_config()
        track_2()
        self.assertEqual(track_2.status_code, 3)
        self.assertEqual(track_2.action_return, 'metal', "ensure that the action executed")
        output = track_2.as_dict()
        self.assertEqual(output['condition_evaluation'], True, "ensure output to dictionary")

    def test_conditional_configured_accession(self):
        """tests the configuredaction condition where the condition is a class flag"""
        cond_class = ConditionClass()
        cond_conf_1 = ConfiguredAction(return_str, condition=(cond_class, 'flag'))
        track_1 = cond_conf_1.get_tracked_from_config()
        track_1()
        self.assertEqual(track_1.status_code, 3)
        self.assertIsNone(track_1.action_return, "ensure that the action didn't run")
        cond_class.flag = True
        track_2 = cond_conf_1.get_tracked_from_config()
        track_2()
        self.assertEqual(track_2.status_code, 3)
        self.assertEqual(track_2.action_return, 'metal', "ensure that the action executed")

    def test_configuration_removal(self):
        """tests removal of a configuration from list"""
        def temporary_action():
            """a temporary action to register"""
            return
        ca = ConfiguredAction(temporary_action, parent_identifier_override='custom parent id')
        self.assertTrue(ca in ConfiguredAction.class_registry, 'ensure action was registered')
        # attempt to remove configured action from registry
        ConfiguredAction.remove_configuration_from_registry(ca.name)
        self.assertTrue(ca in ConfiguredAction.class_registry, 'ensure removal failed due to parent id mismatch')
        ConfiguredAction.remove_configuration_from_registry(ca.name, parent_identifier='custom parent id')
        self.assertFalse(ca in ConfiguredAction.class_registry, 'ensure configured action was removed')


class TestEvalAction(unittest.TestCase):
    def setUp(self) -> None:
        Action.register_action(return_str)
        Action.register_action(return_false)
        EvalAction.register_action(return_true)

    def test_evalaction(self):
        """tests the evalaction class"""
        str_action = ConfiguredAction(Action.register_action('return_str'))
        self.assertFalse(str_action.action.returns_bool)

        true_action = ConfiguredAction(return_true, next_action=str_action)
        self.assertTrue(true_action.action.returns_bool)

        false_action_1 = ConfiguredAction(Action.register_action('return_false'))
        self.assertTrue(false_action_1.action.returns_bool)

        false_action_2 = ConfiguredAction(false_action_1)
        self.assertTrue(false_action_2.action.returns_bool)


class TestDecisions(unittest.TestCase):
    @staticmethod
    def print_false():
        print('this should not be printed')

    @staticmethod
    def print_true():
        print('true')

    @staticmethod
    def print_also_true():
        print('also true')

    @staticmethod
    def return_true(string, **kwargs) -> bool:
        return True

    @staticmethod
    def return_false(string, **kwargs) -> bool:
        return False

    def test_decisionaction(self):
        """test ConfiguredDecision and TrackedDecision classes"""
        # create short sequence/decision tree of actions
        false_next = ConfiguredAction(self.print_false)
        true_next = ConfiguredAction(self.print_true)
        true_eval_action = EvalAction(self.return_true)
        false_eval_action = EvalAction(self.return_false)
        args = ('function returns',)
        true_kwargs = {'next_action': true_next}
        true_action = ConfiguredAction(
            true_eval_action,
            *args,
            **true_kwargs,
        )
        false_kwargs = {'next_action': false_next}
        false_action = ConfiguredAction(
            false_eval_action,
            *args,
            **false_kwargs,
        )
        config_decision = ConfiguredDecision(
            false_action,
            true_action,
            configuration_name='logic checklist'
        )
        # create the decision action and execute it
        decision_action = TrackedDecision(configuration=config_decision)
        self.assertTrue(as_dict_serializable(decision_action))
        decision_action()
        self.assertTrue(as_dict_serializable(decision_action))
        decision_next_action = decision_action.next_action
        self.assertEqual(decision_next_action, true_next)
        # change the next action of true action, make a new decision action and make sure the new next action gets
        # returned correctly
        also_true = ConfiguredAction(self.print_also_true)
        true_action.next_action = also_true
        # ensure that attempts to create a TrackedAction subclass with TrackedAction as the action will error
        self.assertRaises(
            NameError,
            TrackedDecision,
            decision_action
        )
        decision_2 = decision_action.copy_configuration()
        decision_2()
        self.assertEqual(decision_2.action_return, also_true)


class TestTrackedAction(unittest.TestCase):
    def test(self):
        """tests tracked action class"""
        tracked_action = TrackedAction(
            one_second
        )
        self.assertTrue(as_dict_serializable(tracked_action))
        start_time = time.time()
        tracked_action()
        self.assertTrue(as_dict_serializable(tracked_action))
        end_time = time.time()
        self.assertAlmostEqual(
            start_time,
            tracked_action.time_started,
            places=1,
        )
        self.assertAlmostEqual(
            end_time,
            tracked_action.time_completed,
            places=1,
        )
        self.assertAlmostEqual(
            end_time - start_time,
            tracked_action.action_duration,
            places=1,
            )
        self.assertEqual(
            tracked_action.configuration.action.name,
            one_second.__name__
        )
        self.assertEqual(
            tracked_action.action_return,
            one_second_return
        )
        dct = tracked_action.as_dict()  # todo more elaborate test for dict testing

        configured_action_2 = ConfiguredAction(passthrough,
                                               next_action=tracked_action.configuration)
        tracked_action_2 = TrackedAction(
            configured_action_2,
        )
        self.assertEqual(
            f'1: {Status.ACTION_STATES[1]}',
            tracked_action_2.status,
        )
        self.assertEqual(configured_action_2,
                         tracked_action_2.configuration)
        self.assertEqual(configured_action_2.action,
                         tracked_action_2.configuration.action)
        self.assertEqual(configured_action_2.next_action,
                         tracked_action_2.next_action)
        self.assertEqual(ConfiguredAction.ensure_configuration('one_second'),
                         tracked_action_2.next_action)

        tracked_action_3 = tracked_action_2.copy_configuration()
        self.assertEqual(tracked_action_3.configuration, tracked_action_2.configuration)
        self.assertEqual(tracked_action_3.args, tracked_action_2.args)
        self.assertEqual(tracked_action_3.kwargs, tracked_action_2.kwargs)

        self.assertEqual((),
                         tracked_action_2.args)
        args = ('squirrels', )
        tracked_action_2.update_args(*args)
        self.assertEqual(args,
                         tracked_action_2.args)
        kwargs = {'squirrels': 'almonds'}
        tracked_action_2.update_kwargs(**kwargs)
        self.assertEqual(kwargs,
                         tracked_action_2.kwargs)
        tracked_action_2()
        self.assertEqual(
            f'3: {Status.ACTION_STATES[3]}',
            tracked_action_2.status,
        )
        self.assertEqual(True, tracked_action_2.triggered)

        self.assertNotEqual(tracked_action_2.args, tracked_action.args)
        self.assertNotEqual(tracked_action_2.kwargs, tracked_action.kwargs)

    def test_error_catching(self):
        action = Action.register_action(erronious)
        action = TrackedAction(action)
        action()
        self.assertTrue(action.error)
        self.assertEqual(action.error_details.args[0], error_details)
        self.assertEqual(-1, action.status_code)


class TestConfiguration(unittest.TestCase):
    def test_configuration(self):
        """tests the configuration class"""
        test = Configuration(1, 2, 3, a='b', asdf='c')
        self.assertEqual(
            test.args,
            (1, 2, 3)
        )
        test.update_args(2, 3, 4)
        self.assertEqual(
            test.args,
            (2, 3, 4)
        )
        self.assertEqual(
            test.kwargs,
            {'a': 'b', 'asdf': 'c'}
        )
        test.update_kwargs(a='c', ghjk=2)
        self.assertEqual(
            test.kwargs,
            {'a': 'c', 'asdf': 'c', 'ghjk': 2}
        )
        test.freeze = True
        self.assertRaises(
            ValueError,
            test.update_args,
            1
        )


class TestLogic(unittest.TestCase):
    def test_logic(self):
        true_config = ConfiguredAction(return_true)
        false_config = ConfiguredAction(return_false)
        configured_decision = ConfiguredDecision(false_config, true_config)
        # self.assertEqual(  # todo add comparison magic methods to ActionList and derivatives
        #     configured_decision.logic_sequence,
        #     ConfiguredActionList(false_config, true_config)
        # )

        tracked_1 = TrackedDecision(configured_decision)
        tracked_2 = configured_decision.get_tracked_from_config()
        self.assertEqual(
            tracked_1.configuration,
            tracked_2.configuration
        )
        self.assertEqual(
            tracked_1.configuration(),
            tracked_2.configuration()
        )

        kwargs = {'squirrel': 'almonds'}
        tracked_2.update_kwargs(**kwargs)
        self.assertEqual(
            tracked_2.kwargs,
            kwargs
        )
        tracked_3 = configured_decision.get_tracked_from_config(**kwargs)
        self.assertEqual(
            tracked_3.kwargs,
            kwargs
        )

        next_conf = ConfiguredAction(passthrough)
        true_config.next_action = next_conf
        tracked_4 = true_config.get_tracked_from_config()
        self.assertEqual(
            tracked_4.next_action,
            next_conf
        )


class TestOperators(unittest.TestCase):
    def log_1(self, one: str, **kwargs):
        logger.debug(one)
        logger.debug(kwargs)
        return one, kwargs

    def log_2(self, two: str, **kwargs):
        logger.debug(two)
        logger.debug(kwargs)
        return two, kwargs

    def return_bool(self, bool: bool) -> bool:
        return bool

    def test_execute_sequence_actions(self):
        config_log_1 = ConfiguredAction(self.log_1)
        config_log_2 = ConfiguredAction(self.log_2)
        tracked_1 = config_log_1.get_tracked_from_config()
        tracked_2 = config_log_2.get_tracked_from_config()
        kwargs = {'log_1': {'one': 'one!',
                            'kwargs': 'kwargs for one'},
                  'log_2': {'two': 'two!',
                            'kwargs': 'kwargs for two'}
                  }

        tracked_actions = [tracked_1, tracked_2]
        execute_sequence_actions(*tracked_actions, **kwargs)
        self.assertEqual(False,
                         tracked_1.error,
                         )
        self.assertEqual(False,
                         tracked_2.error,
                         )
        self.assertEqual(
            ('one!', {'kwargs': 'kwargs for one'}),
            tracked_1.action_return)
        self.assertEqual(
            ('two!', {'kwargs': 'kwargs for two'}),
            tracked_2.action_return)

        # cannot execute a tracked action more than once
        self.assertRaises(
            RuntimeError,
            execute_sequence_actions,
            *tracked_actions, **kwargs,
        )

    def test_decision(self):
        config_log_1 = ConfiguredAction(self.log_1)
        config_log_2 = ConfiguredAction(self.log_2)

        eval_action = EvalAction(self.return_bool)
        conf_true = ConfiguredAction(eval_action, next_action=config_log_1, **{'bool': True})
        conf_false = ConfiguredAction(eval_action, next_action=config_log_2, **{'bool': False})

        tracked_true = conf_true.get_tracked_from_config()
        tracked_false = conf_false.get_tracked_from_config()
        logic_checks = [tracked_false, tracked_true]

        # todo should there be a way to pass kwargs to a decision or not?
        decision_next = decision(*logic_checks)
        self.assertTrue(tracked_true.triggered)
        self.assertTrue(tracked_false.triggered)
        self.assertEqual(config_log_1,
                         decision_next)

    def test_run_automation(self):
        config_log_1 = ConfiguredAction(self.log_1, configuration_name='uta')
        config_log_2 = ConfiguredAction(self.log_2, configuration_name='eluveitie')

        first_action = ConfiguredAction(self.log_1,
                                        configuration_name='first action',
                                        **{'one': 'first one'}
                                        )

        eval_action = EvalAction.register_action(self.return_bool)
        conf_true = ConfiguredAction(eval_action, next_action=config_log_1, **{'bool': True})
        conf_false = ConfiguredAction(eval_action, next_action=config_log_2, **{'bool': False})

        configured_decision = ConfiguredDecision(conf_false, conf_true)
        first_action.next_action = configured_decision

        kwargs = {'uta': {'one': 'one!',
                          'kwargs': 'kwargs for one'},
                  'eluveitie': {'two': 'two!',
                                'kwargs': 'kwargs for two'}
                  }
        executed_actions = run_automation(first_action, **kwargs)
        self.assertEqual(3,
                         len(executed_actions))

        self.assertTrue(first_action.status)
        tracked_first_action = executed_actions[0]
        tracked_decision = executed_actions[1]
        tracked_conf_log_1 = executed_actions[2]  # this was the next action from the decision
        self.assertEqual(('first one', {}),
                         tracked_first_action.action_return)
        self.assertEqual(config_log_1,
                         tracked_decision.action_return)
        self.assertEqual(('one!', {'kwargs': 'kwargs for one'}),
                         tracked_conf_log_1.action_return)


class RegMethodsInstance(ConfigurableInstance):
    methods_to_register = [
        'inst_action_one',
        'inst_action_two',
    ]

    def __init__(self):
        ConfigurableInstance.__init__(self, instance_specific_actions=True)

    def inst_action_one(self):
        return 'banana'

    def inst_action_two(self):
        return 'split'


class TestConfigurableInstance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_inst = RegMethodsInstance()
        cls.test_inst2 = RegMethodsInstance()

    def test_registered(self):
        """tests that methods are registered"""
        self.assertTrue(isinstance(self.test_inst.inst_action_one, ConfiguredAction))
        self.assertTrue(isinstance(self.test_inst.inst_action_two, ConfiguredAction))

    def test_blocking_exec(self):
        """tests blocking execution"""
        def execute_and_test(action, result):
            ta = self.test_inst.execute_action(action)
            self.assertEqual(ta.status_code, 3)
            self.assertEqual(ta.action_return, result)
        execute_and_test('inst_action_one', 'banana')
        execute_and_test('inst_action_two', 'split')

    def test_nonblocking_exec(self):
        """tests threaded execution of actions"""
        def execute_and_test(action, result):
            tta = self.test_inst.execute_action_threaded(action)
            tta.wait_for_completion()
            self.assertEqual(tta.status_code, 3)
            self.assertEqual(tta.action_return, result)

        execute_and_test('inst_action_one', 'banana')
        execute_and_test('inst_action_two', 'split')

    def test_method_associations(self):
        """tests that registered methods of a class are not methods of the other"""
        self.assertFalse(
            self.test_inst.inst_action_one is self.test_inst2.inst_action_one,
            "ensure configured actions are not duplicates"
        )
        self.assertFalse(
            self.test_inst.inst_action_one.action.action
            is self.test_inst2.inst_action_one.action.action,
            "ensure actions point to correct instance"
        )
