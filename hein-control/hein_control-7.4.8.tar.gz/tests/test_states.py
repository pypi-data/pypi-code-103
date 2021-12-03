import threading
import time
import unittest
import operator
from hein_control.states import (ComponentState, OperationalState, ensure_component_online, ensure_component_inactive,
                                 BadComponentState, GenericActionState, TemporaryOperationalCallback,
                                 TemporaryActionCallback)
from hein_control.states.abc import State, StateSet
from hein_control.action.configured import ConfiguredAction


class CustomOperationalState(StateSet):
    ERROR = State(-1)
    OFFLINE = State(0)
    ONLINE = State(1)
    AMAZING = State(2)


class CustomActiveState(StateSet):
    IDLE = State(0)
    ACTIVE = State(1)
    HYPERACTIVE = State(2)
    JUMP_JUMP = 3
    BOOGIE_WOOGIE = State(4)
    # can you tell I have a two year old?


class TestComponent(ComponentState):
    action_states = CustomActiveState
    operational_states = CustomOperationalState

    @ensure_component_online
    def only_run_online(self):
        return

    @ensure_component_inactive
    def only_run_inactive(self):
        return


class TestComponentStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = threading.Lock()
        cls.component_one = TestComponent('test_component1', 1)
        cls.component_two = ComponentState('test_component2', 1)
        cls.component_three = ComponentState('test_component3', 1)

    def set_and_check_state(self, component: ComponentState, attribute: str, state: StateSet):
        """generic tester for action and operational state"""
        # test by value
        setattr(component, attribute, state.value)
        self.assertIs(getattr(component, attribute), state)
        # test by name
        setattr(component, attribute, state.name)
        self.assertIs(getattr(component, attribute), state)
        # test name capitalization support
        setattr(component, attribute, state.name.lower())
        self.assertIs(getattr(component, attribute), state)
        # test direct state setting
        setattr(component, attribute, state)
        self.assertIs(getattr(component, attribute), state)

    def set_and_check_operational_state(self, component: ComponentState, state: OperationalState):
        """tests the setting of an operational state by state, value, and name"""
        # test property setting
        self.set_and_check_state(component, 'current_operational_state', state)
        # test method updating
        component.update_operational_state(state)
        self.assertIs(component.current_operational_state, state)

    def set_and_check_action_state(self, component: ComponentState, state: OperationalState):
        """tests the setting of an active state by state, value, and name"""
        # test property setting
        self.set_and_check_state(component, 'current_action_state', state)
        # test method updating
        component.update_action_state(state)
        self.assertIs(component.current_action_state, state)

    def test_component_state_setting(self):
        """tests setting and retrieval of component states"""
        with self.lock:
            for state in CustomOperationalState:
                self.set_and_check_operational_state(self.component_one, state)

    def test_online_only(self):
        """tests the online check decorator functionality"""
        with self.lock:
            try:
                # check that the method runs
                self.component_one.only_run_online()
                # set to offline state
                self.component_one.current_operational_state = 0
                self.assertRaises(BadComponentState, self.component_one.only_run_online)
                # set to error state
                self.component_one.current_operational_state = -1
                self.assertRaises(BadComponentState, self.component_one.only_run_online)
            finally:
                self.component_one.current_operational_state = OperationalState.ONLINE

    def test_component_activity_setting(self):
        """tests the setting of the component activity"""
        with self.lock:
            for state in GenericActionState:
                self.set_and_check_action_state(self.component_two, state)

    def test_custom_activity_setting(self):
        """tests components with custom activity support"""
        with self.lock:
            for state in CustomActiveState:
                self.set_and_check_action_state(self.component_one, state)

    def test_inactive_only(self):
        """tests the inactive-only decorator functionality"""
        with self.lock:
            try:
                # set to active state
                for state in CustomActiveState:
                    self.component_one.current_action_state = state
                    if state == 0:
                        # check that the method runs
                        self.component_one.only_run_inactive()
                    else:
                        self.assertRaises(BadComponentState, self.component_one.only_run_inactive)
            finally:
                self.component_one.current_action_state = 0

    def update_component_state(self, state):
        """sets component one to an error state after 1 second"""
        time.sleep(1)
        self.component_one.current_operational_state = state

    def get_component_state_thread(self, state: int = -1):
        """retrieves a thread which sets the first component to the specified state"""
        return threading.Thread(
            target=self.update_component_state,
            daemon=True,
            args=[state],
        )

    def update_component_action_state(self, state):
        """sets the component action to the defined state after 1 second"""
        time.sleep(1.)
        self.component_one.current_action_state = state

    def get_component_action_state_thread(self, state: int = -1):
        """retrieves a thread which sets the first component to the specified state"""
        return threading.Thread(
            target=self.update_component_action_state,
            daemon=True,
            args=[state],
        )

    def test_self_waiting(self):
        """tests waiting on a component where the error flag is switched mid-wait"""
        with self.lock:
            try:
                # ensure state monitor actually sleeps
                self.component_one.components_state_monitor_sleep(0.1)
                # tests that error raises
                first_thread = self.get_component_state_thread()
                first_thread.start()
                self.assertRaises(
                    BadComponentState,
                    self.component_one.components_state_monitor_sleep,
                    2
                )

            finally:
                self.component_one.current_operational_state = 1

    def test_adjacent_waiting(self):
        """tests a wait where the error flag is flipped on another component"""
        with self.lock:
            try:
                # ensure state monitor actually sleeps
                self.component_two.components_state_monitor_sleep(0.1)
                # perform wait on another component and ensure that bad state propagates to an error
                second_thread = self.get_component_state_thread()
                second_thread.start()
                self.assertRaises(
                    BadComponentState,
                    self.component_two.components_state_monitor_sleep,
                    2
                )

            finally:
                self.component_one.current_operational_state = 1

    def test_solo_monitor(self):
        """tests a wait where a single component is monitored for an error state (ignores errors from other components"""
        with self.lock:
            try:
                # perform wait on an third component, specifically only monitoring that component
                #   component 1 is still in an error state for this test
                third_thread = self.get_component_state_thread()
                third_thread.start()
                self.component_three.components_state_monitor_sleep(
                    1.5,
                    'test_component3'
                )
            finally:
                self.component_one.current_operational_state = 1

    def test_wait_for_operational(self):
        """tests the functionality for waiting for a component to be operational"""
        with self.lock:
            try:
                # set to offline
                self.component_one.current_operational_state = 0
                thread = self.get_component_state_thread(1)
                thread.start()
                self.component_one.wait_for_component_operational_state(1)

                # test timeout
                self.component_one.current_operational_state = 0
                self.assertRaises(
                    TimeoutError,
                    self.component_one.wait_for_component_operational_state,
                    1,
                    timeout=0.5,
                )

            finally:
                self.component_one.current_operational_state = 1

    def test_wait_for_action(self):
        """tests the functionality for waiting for a component to be ___"""
        with self.lock:
            try:
                self.component_one.current_action_state = 0
                thread = self.get_component_action_state_thread(1)
                thread.start()
                self.component_one.wait_for_component_action_state(1)

                # test timeout
                self.component_one.current_action_state = 0
                self.assertRaises(
                    TimeoutError,
                    self.component_one.wait_for_component_action_state,
                    1,
                    timeout=0.5,
                )

            finally:
                self.component_one.current_action_state = 0

    def test_timeout(self):
        """tests the timeout functionality for the flag check wait"""
        def always_false():
            """Always blue! Always blue! Always blue! Always blue! Always blue!"""
            return False
        with self.lock:
            self.assertRaises(
                TimeoutError,
                self.component_one.state_monitor_flag_check,
                always_false,
                timeout=1.
            )
            # ensure that the function runs without a timeout specified
            self.component_one.state_monitor_flag_check(
                always_false,
                target_flag_state=False,
            )

    def test_action_state_retrieval(self):
        """tests internal aciton state retrieval"""
        for action_state in self.component_one.action_states:
            action_state: StateSet
            for key in [
                action_state,
                action_state.value,
                action_state.name,
                action_state.value.value if isinstance(action_state.value, State) else action_state.value,
            ]:
                self.assertIs(
                    self.component_one.get_action_state_from_key(key),
                    action_state,
                    f'check retrieval of {key}'
                )

    def test_operational_state_retrieval(self):
        """tests internal aciton state retrieval"""
        for action_state in self.component_one.operational_states:
            action_state: StateSet
            for key in [
                action_state,
                action_state.value,
                action_state.name,
                action_state.value.value if isinstance(action_state.value, State) else action_state.value,
            ]:
                self.assertIs(
                    self.component_one.get_operational_state_from_key(key),
                    action_state,
                    f'check retrieval of {key}'
                )

    def test_action_comparison_operator_override(self):
        """tests the comparison operator override capability for the action wait"""
        with self.lock:
            # test eq logic (simulates waiting for an action state to be in a specific place)
            comp_operator = operator.eq
            self.component_one.current_action_state = 0
            thread = self.get_component_action_state_thread(2)
            thread.start()
            self.assertRaises(
                TimeoutError,
                self.component_one.wait_for_component_action_state,
                desired_state=1,
                timeout=0.5,
                comparison_operator=comp_operator,

            )
            self.component_one.current_action_state = 0
            thread = self.get_component_action_state_thread(2)
            thread.start()
            self.component_one.wait_for_component_action_state(2, timeout=1.5, comparison_operator=comp_operator)

            # test lt logic (simulates waiting for an action state to indicate idle)
            comp_operator = operator.le
            self.assertRaises(
                TimeoutError,
                self.component_one.wait_for_component_action_state,
                0,
                timeout=0.5,
                comparison_operator=comp_operator,
            )
            thread = self.get_component_action_state_thread(0)
            thread.start()
            self.component_one.wait_for_component_action_state(
                0,
                timeout=1.5,
                comparison_operator=comp_operator,
            )

    def test_operational_comparison_operator_override(self):
        """tests the comparison operator override capability for the operational state wait"""
        with self.lock:
            # test eq logic (simulates waiting for an action state to be in a specific place)
            comp_operator = operator.eq
            self.component_one.current_operational_state = 0
            thread = self.get_component_state_thread(2)
            thread.start()
            self.assertRaises(
                TimeoutError,
                self.component_one.wait_for_component_operational_state,
                desired_state=1,
                timeout=0.5,
                comparison_operator=comp_operator,

            )
            self.component_one.current_operational_state = 0
            thread = self.get_component_state_thread(2)
            thread.start()
            self.component_one.wait_for_component_operational_state(2, timeout=1.5, comparison_operator=comp_operator)

            # test lt logic (simulates waiting for an action state to indicate idle)
            comp_operator = operator.le
            self.assertRaises(
                TimeoutError,
                self.component_one.wait_for_component_operational_state,
                0,
                timeout=0.5,
                comparison_operator=comp_operator,
            )
            thread = self.get_component_state_thread(0)
            thread.start()
            self.component_one.wait_for_component_operational_state(
                0,
                timeout=1.5,
                comparison_operator=comp_operator,
            )
            self.component_one.current_operational_state = 1


class TestStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_state_one = State(1)

    def test_meaning(self):
        """tests meaning setting of the State class"""
        string = 'test meaning string (docstring) for the state'
        state = State(1, meaning=string)
        self.assertTrue(hasattr(state, 'meaning'), 'ensure that a meaning was assigned')
        self.assertEqual(state.meaning, string, 'check that the state was correctly assigned')

    def test_comparisons(self):
        """tests integer state comparisons"""
        self.assertTrue(1 == self.test_state_one, 'check eq')
        self.assertTrue(2 > self.test_state_one, 'check gt')
        self.assertTrue(1 >= self.test_state_one, 'check ge eq')
        self.assertTrue(2 >= self.test_state_one, 'check ge gt')
        self.assertTrue(0 < self.test_state_one, 'check lt')
        self.assertTrue(1 <= self.test_state_one, 'check le eq')
        self.assertTrue(0 <= self.test_state_one, 'check le lt')

    def test_state_comparisons(self):
        """tests comparisons between State classes"""
        self.assertTrue(State(1) == self.test_state_one, 'check eq')
        self.assertTrue(State(2) > self.test_state_one, 'check gt')
        self.assertTrue(State(1) >= self.test_state_one, 'check ge eq')
        self.assertTrue(State(2) >= self.test_state_one, 'check ge gt')
        self.assertTrue(State(0) < self.test_state_one, 'check lt')
        self.assertTrue(State(1) <= self.test_state_one, 'check le eq')
        self.assertTrue(State(0) <= self.test_state_one, 'check le lt')

    def test_callbacks(self):
        """tests state callback de/registration and execution"""
        def banana():
            return 1234

        def melon():
            return 'asdf'

        # test registration
        self.test_state_one.register_callbacks(banana)
        self.test_state_one.register_post_state_callbacks(melon)
        self.assertEqual(len(self.test_state_one.pre_state_callbacks), 1, "ensure callback was added")
        self.assertEqual(len(self.test_state_one.post_state_callbacks), 1, 'ensure post callback was added')
        self.assertRaises(TypeError, self.test_state_one.register_callbacks, 1, 'check that non-callables are rejected')

        # test execution
        values = self.test_state_one.execute_pre_state_callbacks()
        self.assertEqual(len(values), 1, 'check that two returns were captured')
        self.assertEqual(values[0].action_return, 1234, 'check that first function value is correct')
        post_values = self.test_state_one.execute_post_state_callbacks()
        self.assertEqual(post_values[0].action_return, 'asdf', 'check that second function value is correct')

        # test deregistration
        self.test_state_one.deregister_callbacks(banana)
        self.assertEqual(len(self.test_state_one.pre_state_callbacks), 0, 'ensure callback was removed')
        self.assertFalse(self.test_state_one.has_pre_state_change_callbacks, 'ensure pre-state-change callback was removed')
        self.assertTrue(self.test_state_one.has_post_state_change_callbacks, 'ensure post-state-change callback was unaffected')
        self.assertFalse(banana in self.test_state_one.pre_state_callbacks, 'check that method was deregistered')

        self.test_state_one.deregister_callbacks(melon)
        self.assertFalse(self.test_state_one.has_callbacks)
        self.assertFalse(self.test_state_one.has_post_state_change_callbacks)
        self.assertFalse(self.test_state_one.has_pre_state_change_callbacks)


class FancyOperationalStates(StateSet):
    CRAZY_BAD = State(-9000)
    BAD = State(-1)
    OFFLINE = 0
    GOOD = State(1)
    GREAT = State(2)


class FancyTestComponent(ComponentState):
    operational_states = FancyOperationalStates

    bad_string = 'omg this super bad thing happened'
    good_string = 'never mind, things are fine'
    no_change = 'no change needed'
    allowable_jump = 'sure, you can do that'

    def __init__(self):
        """a test component which has """
        super(FancyTestComponent, self).__init__('fancy_test_component')
        self.real_bad_thing_happened = False
        self.operational_states.BAD.register_callbacks(self.critical_action)
        self.operational_states.GOOD.register_callbacks(self.restore_functionality)
        self.operational_states.CRAZY_BAD.register_callbacks(self.check_operational_state_jump)
        self.action_states.ACTIVE.register_callbacks(self.check_action_state_jump)

    def critical_action(self):
        """registers that a critical thing has happened"""
        self.real_bad_thing_happened = True
        return self.bad_string

    def restore_functionality(self):
        """restores functionality after a critical thing has happened"""
        if self.current_operational_state > 0:
            return self.no_change
        self.real_bad_thing_happened = False
        return self.good_string

    def check_operational_state_jump(self):
        """will raise an error if the state was already changed"""
        if self.current_operational_state == -9000:
            raise ValueError('this error will occur only if the state is changed before the callbacks are executed')
        return self.allowable_jump

    def check_action_state_jump(self):
        """will raise an error if the state was already changed"""
        if self.current_action_state == 1:
            raise ValueError('this error will occur only if the state is changed before the callbacks are executed')
        return self.allowable_jump


class TestComponentCallbacks(unittest.TestCase):
    """Tests automatic callback execution component state switching"""
    @classmethod
    def setUpClass(cls) -> None:
        cls.component = FancyTestComponent()
        cls.lock = threading.Lock()

    def test_registration(self):
        """ensure actions were registered as expected"""
        self.assertIsNotNone(
            self.component.operational_states.BAD.value.pre_state_callbacks.get_ca_by_action(
                self.component.critical_action
            )
        )
        self.assertTrue(
            self.component.operational_states.GOOD.value.pre_state_callbacks.get_ca_by_action(
                self.component.restore_functionality
            )
        )

    def test_callback_functionality(self):
        """tests callback functionality"""
        with self.lock:
            try:
                # change the operational state to a bad state; ensure callback was executed
                value = self.component.update_operational_state(-1)
                self.assertEqual(value[0].action_return, self.component.bad_string, 'ensure return value is captured')
                self.assertTrue(self.component.real_bad_thing_happened, 'ensure callback executed as expected')

                # change the operational state to a good one; ensure callback was executed
                value = self.component.update_operational_state(1)
                self.assertEqual(value[0].action_return, self.component.good_string, 'ensure return value is captured')
                self.assertFalse(self.component.real_bad_thing_happened, 'ensure callback executed as expected')

                # test condition check within restor function
                value = self.component.update_operational_state(1)
                self.assertEqual(value[0].action_return, self.component.no_change, 'ensure conditional checks work')

                # these will fail if the state is updated before the callbacks are executed
                value = self.component.update_operational_state(-9000)
                self.assertEqual(value[0].action_return, self.component.allowable_jump)
                value = self.component.update_action_state(1)
                self.assertEqual(value[0].action_return, self.component.allowable_jump)
            finally:
                self.component.update_operational_state(1)
                self.component.update_action_state(0)

    def pre_state_check_callback(self):
        """special callback which should be executed before a component state is changed"""
        self.assertEqual(self.component.current_operational_state, 1)

    def post_state_check_callback(self):
        """special callback which should be executed after a component state is changed"""
        self.assertEqual(self.component.current_operational_state, 2)

    def test_operational_callback_ordering(self):
        """
        tests that pre- and post- operational state change callbacks are executed in the correct place
        """
        with self.lock:
            try:
                self.component.update_operational_state(1)  # start from 1
                state = self.component.operational_states(2)
                state.register_pre_state_callbacks(self.pre_state_check_callback)
                state.register_post_state_callbacks(self.post_state_check_callback)
                self.component.update_operational_state(2)
                # deregister and check
                state.deregister_callbacks(self.pre_state_check_callback, self.post_state_check_callback)
                self.assertFalse(self.pre_state_check_callback in state.value.pre_state_callbacks)
                self.assertFalse(self.post_state_check_callback in state.value.post_state_callbacks)
            finally:
                self.component.update_operational_state(1)
                self.component.update_action_state(0)

    def pre_action_state_check_callback(self):
        """special callback which should be executed before a component state is changed"""
        self.assertEqual(self.component.current_action_state, 0)

    def post_action_state_check_callback(self):
        """special callback which should be executed after a component state is changed"""
        self.assertEqual(self.component.current_action_state, 1)

    def test_alias_setting(self):
        """tests alias setting for a state"""
        state = State(1, alias='banana')
        self.assertEqual(state.alias, 'banana', 'test alias was set from instantiation')
        state.alias = 'melon'
        self.assertEqual(state.alias, 'melon', 'test alias updating')

        class TestStateSet(StateSet):
            MELON = State(1)
            BANANA = 2

        test_state = TestStateSet(1)
        self.assertEqual(test_state.name, 'MELON', 'test base name')
        self.assertEqual(test_state.get_name(), 'MELON', 'test default')
        self.assertEqual(TestStateSet(2).get_name(), 'BANANA', 'test name retrieval from integer')
        test_state.set_alias('delicious')
        self.assertEqual(test_state.value.alias, 'delicious', 'test alias setting passthrough')
        self.assertEqual(test_state.get_name(), 'delicious', 'test name retrieval is updated')

    def test_action_callback_ordering(self):
        """
        tests that pre- and post- operational state change callbacks are executed in the correct place
        """
        with self.lock:
            try:
                self.component.update_action_state(0)
                state = self.component.action_states(1)
                state.register_pre_state_callbacks(self.pre_action_state_check_callback)
                state.register_post_state_callbacks(self.post_action_state_check_callback)
                self.component.update_action_state(1)
                # deregister and check
                state.deregister_callbacks(self.pre_action_state_check_callback, self.post_action_state_check_callback)
                self.assertFalse(self.pre_action_state_check_callback in state.value.pre_state_callbacks)
                self.assertFalse(self.post_action_state_check_callback in state.value.post_state_callbacks)
            finally:
                self.component.update_operational_state(1)
                self.component.update_action_state(0)

    def test_callback_deletion(self):
        """tests deletion functionality of callbacks"""
        def some_one_off_function():
            pass
        with self.lock:
            self.component.operational_states(1).value.register_callbacks(some_one_off_function)
            ca = self.component.operational_states(1).value.pre_state_callbacks[-1]
            self.assertIsNotNone(ConfiguredAction.class_instance_by_id(ca.name), 'check that retrieval works')
            self.component.operational_states(1).value.deregister_callbacks(
                some_one_off_function,
                remove_configurations=True,
            )
            self.assertNotIn(
                ca, self.component.operational_states(1).value.pre_state_callbacks,
                'ensure method was removed from callback list'
            )
            self.assertRaises(  # ensure that the configured action was removed as expected
                NameError,
                ConfiguredAction.class_instance_by_id,
                ca.name,
            )


class SoManyStates(StateSet):
    SUPER_BAD = State(-10)
    QUITE_BAD = State(-2)
    BAD = State(-1)
    NOT_GREAT = State(0)
    OK = State(1)
    GOOD = State(2)
    GREAT = State(3)
    EXCELLENT = State(10)


class AllTheStates(ComponentState):
    operational_states = SoManyStates
    action_states = CustomActiveState


class TestTemporaryCallback(unittest.TestCase):
    change_state_wait_return = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.component = AllTheStates('so many states')
        cls.lock = threading.Lock()

    @staticmethod
    def custom_callback():
        raise ValueError('oh no the worst thing has happened!')

    def check_assigned(self, fn, threshold=0):
        """performs the appropriate assignment checks depending on the threshold state"""
        for state in self.component.operational_states:
            if state <= threshold:
                self.assertTrue(state.has_callbacks, f'ensure a callback is assigned to {state}')
                self.assertTrue(
                    state.value.pre_state_callbacks.action_registered_in_list(fn),
                    f'ensure correct callback was assigned to {state}'
                )
            else:
                self.assertFalse(state.has_callbacks, 'ensure callback was not assigned to states above threshold')
                self.assertFalse(
                    state.value.pre_state_callbacks.action_registered_in_list(fn),
                    f'ensure callback was not assigned to {state}'
                )

    def check_unassigned(self, fn):
        """performs a check to ensure that the provided function has been unassigned from all component operational states"""
        for state in self.component.operational_states:
            self.assertFalse(state.has_callbacks, f'ensure no callbacks are registered to {state}')

    def test_default_callback(self):
        """tests setting of the default callback method"""
        with self.lock:
            try:
                with TemporaryOperationalCallback(self.component) as tcb:
                    self.assertIsInstance(tcb, TemporaryOperationalCallback, 'ensure callback TemporaryOperationalCallback instance is returned')
                    self.check_assigned(tcb.callback_capture)
                    self.component.update_operational_state(-1)
                    self.assertTrue(tcb.callback_encountered, 'ensure callback was encountered')
                for state in self.component.operational_states:
                    self.assertFalse(
                        tcb.callback_capture in state.value.pre_state_callbacks,
                        'ensure callback was removed'
                    )
                    self.assertFalse(state.has_callbacks)
            finally:
                self.component.update_operational_state(1)

    def test_threshold_setting(self):
        """tests that the callback was only applied to states at or below the threshold"""
        with self.lock:
            for threshold_state in self.component.operational_states:
                with TemporaryOperationalCallback(self.component, threshold_state=threshold_state) as tcb:
                    self.check_assigned(tcb.callback_capture, threshold_state)
                self.check_unassigned(tcb.callback_capture)

    def test_custom_callback(self):
        """tests custom callback setting"""
        with self.lock:
            try:
                with TemporaryOperationalCallback(self.component, callbacks=self.custom_callback) as tcb:
                    self.check_assigned(self.custom_callback)
                    self.change_state_wait()
                    self.assertIsNotNone(self.change_state_wait_return)
                    # load specific tracked actions
                    callback_capture, custom_callback = self.change_state_wait_return
                    self.assertEqual(callback_capture.status_code, 3, 'ensure callback capture was triggered')
                    self.assertEqual(custom_callback.status_code, -1, 'ensure error was raised by custom callback')
                    self.assertIsNotNone(custom_callback.error_details, 'ensure error details were set')
                    self.assertIsInstance(custom_callback.error_details, ValueError, 'ensure details are error instance')

                self.assertTrue(tcb.callback_encountered)
                # ensure callback was unassigned after exiting
                for state in self.component.operational_states:
                    self.assertFalse(state.has_callbacks)
                    self.assertFalse(tcb.callback_capture in state.value.pre_state_callbacks)
            finally:
                self.component.update_operational_state(1)

    def change_state_wait(self):
        """
        waits for some time and changes the component operational state. This should trigger an error if it is executed
        inside a TCB context
        """
        time.sleep(0.1)
        self.change_state_wait_return = self.component.update_operational_state(-1)

    def check_registered(self, lst, fn):
        """checks that the provided callable was registered in the provided ConfiguredActionList"""
        self.assertTrue(
            lst.action_registered_in_list(fn),
            f'ensure {fn} is registered in {lst}'
        )

    def check_not_registered(self, lst, fn):
        """checks that the provided callable is not registered in the provided ConfiguredActionList"""
        self.assertFalse(
            lst.action_registered_in_list(fn),
            f'ensure {fn} is not registered in {lst}'
        )

    def test_action_callback(self):
        """tests action callback setting"""
        threshold_state = self.component.action_states(2)
        with TemporaryActionCallback(self.component, callbacks=[self.custom_callback], threshold_state=threshold_state) as tcb:
            self.assertIsInstance(tcb, TemporaryActionCallback, 'ensure TemporaryActionCallback is returned')
            for state in self.component.action_states:
                if state <= threshold_state:
                    self.assertTrue(state.has_callbacks, f'ensure callback was assigned to {state}')
                    self.check_registered(state.value.pre_state_callbacks, self.custom_callback)
                elif hasattr(state.value, 'callbacks'):
                    self.assertFalse(state.has_callbacks, 'ensure callback was not assigned to states above threshold')
                    self.check_not_registered(state.value.pre_state_callbacks, self.custom_callback)

    def test_alias_retrieval(self):
        """tests retrieval of a ComponentState by a state alias"""
        state = self.component.operational_states.NOT_GREAT
        alias = 'so_so'
        state.set_alias(alias)
        self.assertIs(state, self.component.operational_states(alias), 'test retrieval of StateSet by alias')
        self.assertIs(state, self.component.operational_states(state.name), 'ensure retrieval by formal name still works')

    def test_action_removal(self):
        """tests action removal of temporary callbacks"""
        def some_other_action():
            pass

        with TemporaryOperationalCallback(self.component,
                                          callbacks=[some_other_action],
                                          remove_configurations_on_exit=True
                                          ) as tcb:
            capture_action_name = self.component.operational_states(0).value.pre_state_callbacks[0].name
            other_action_name = self.component.operational_states(0).value.pre_state_callbacks[1].name
            self.assertIsNotNone(ConfiguredAction.class_instance_by_id(capture_action_name))
            self.assertIsNotNone(ConfiguredAction.class_instance_by_id(other_action_name))

        # ensure that actions have been fully deregistered
        self.assertRaises(
            NameError,
            ConfiguredAction.class_instance_by_id,
            capture_action_name
        )
        self.assertRaises(
            NameError,
            ConfiguredAction.class_instance_by_id,
            other_action_name,
        )
