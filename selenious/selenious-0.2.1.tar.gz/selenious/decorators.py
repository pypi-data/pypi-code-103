from selenium.common.exceptions import NoSuchElementException
import functools
from time import sleep, monotonic
from .helpers import validate_time_settings
from .recover import RecoverData, RecoverFuncId


def _find_element_next_state(prev_state, time_left, poll_frequency):
    if time_left <= 0:
        if prev_state is None:
            return ("recover_or_raise", 0)
        else:
            return ("raise", None)

    return ("recover_and_retry", min(time_left, poll_frequency))


def find_element(func):
    special_args = ("timeout", "poll_frequency", "recover")

    @functools.wraps(func)
    def find_element_decorator(self, *args, **kwargs):
        func_kwargs = {k: v for (k, v) in kwargs.items() if k not in special_args}
        timeout = kwargs.get("timeout", self.timeout)
        poll_frequency = kwargs.get("poll_frequency", self.poll_frequency)
        recover = kwargs.get("recover", self.recover)
        start_time = monotonic()
        state = None
        attempts = 0

        validate_time_settings(self._implicitly_wait, timeout, poll_frequency)

        while True:
            exception = None
            try:
                from .webelement import SeleniousWrapWebElement

                return SeleniousWrapWebElement(func(self, *args, **func_kwargs))
            except NoSuchElementException as e:
                timestamp = monotonic()
                time_left = timeout + start_time - timestamp
                state, sleep_time = _find_element_next_state(
                    prev_state=state, time_left=time_left, poll_frequency=poll_frequency
                )
                if state == "raise" or (state == "recover_or_raise" and not recover):
                    raise
                exception = e

            attempts += 1
            if recover:
                save = self.recover
                self.recover = None
                from .webdriver_mixin import WebDriverMixin

                if isinstance(self, WebDriverMixin):
                    webdriver = self
                    element = None
                    func_id = RecoverFuncId.FIND_ELEMENT
                else:
                    webdriver = self.parent
                    element = self
                    func_id = RecoverFuncId.ELEMENT_FIND_ELEMENT

                recover_data = RecoverData(
                    webdriver=webdriver,
                    element=element,
                    func_id=func_id,
                    function=func,
                    args=args,
                    kwargs=kwargs,
                    elapsed=timestamp - start_time,
                    attempts=attempts,
                    exception=exception,
                )
                try:
                    recover(recover_data)
                except:  # noqa E722
                    self.recover = save
                    raise
                self.recover = save
            sleep(sleep_time)

    return find_element_decorator


def _find_elements_next_state(
    prev_state,
    time_left,
    poll_frequency,
    debounce,
    stable_time,
    ismin,
):
    if ismin:
        settle_time_remaining = debounce - stable_time
        if settle_time_remaining > 0:
            return ("debounce", settle_time_remaining)
        else:
            return ("success", None)

    if time_left <= 0:
        if prev_state is None:
            return ("recover_or_raise", 0)
        else:
            return ("raise", None)

    return ("recover_and_retry", min(time_left, poll_frequency))


def find_elements(func):

    special_args = ("timeout", "poll_frequency", "recover", "min", "debounce")

    @functools.wraps(func)
    def find_elements_decorator(self, *args, **kwargs):
        func_kwargs = {k: v for (k, v) in kwargs.items() if k not in special_args}
        timeout = kwargs.get("timeout", self.timeout)
        poll_frequency = kwargs.get("poll_frequency", self.poll_frequency)
        recover = kwargs.get("recover", self.recover)
        min = kwargs.get("min", 0)
        debounce = kwargs.get("debounce", self.debounce)
        debounce = poll_frequency if debounce is True else debounce
        start_time = monotonic()
        attempts = 0
        prev_len = 0
        prev_time = start_time
        state = None

        validate_time_settings(self._implicitly_wait, timeout, poll_frequency)

        while True:
            retval = func(self, *args, **func_kwargs)
            timestamp = monotonic()
            attempts += 1
            length = len(retval)
            if length != prev_len:
                prev_time = timestamp
                prev_len = length
                stable_time = 0
            else:
                stable_time = timestamp - prev_time
            time_left = timeout + start_time - timestamp
            ismin = prev_len >= min

            state, sleep_time = _find_elements_next_state(
                prev_state=state,
                time_left=time_left,
                poll_frequency=poll_frequency,
                debounce=debounce,
                stable_time=stable_time,
                ismin=ismin,
            )

            if state == "success":
                from .webelement import SeleniousWrapWebElement

                return [SeleniousWrapWebElement(e) for e in retval]

            if state == "raise" or (state == "recover_or_raise" and not recover):
                raise NoSuchElementException(
                    "{} elements is less than min of {}".format(length, min)
                )

            if state in ("recover_or_raise", "recover_and_retry") and recover:
                save = self.recover
                self.recover = None
                from .webdriver_mixin import WebDriverMixin

                if isinstance(self, WebDriverMixin):
                    webdriver = self
                    element = None
                    func_id = RecoverFuncId.FIND_ELEMENTS
                else:
                    webdriver = self.parent
                    element = self
                    func_id = RecoverFuncId.ELEMENT_FIND_ELEMENTS
                recover_data = RecoverData(
                    webdriver=webdriver,
                    func_id=func_id,
                    function=func,
                    element=element,
                    args=args,
                    kwargs=kwargs,
                    elapsed=timestamp - start_time,
                    attempts=attempts,
                    elements=retval,
                )
                try:
                    recover(recover_data)
                except:  # noqa E722
                    self.recover = save
                    raise

                self.recover = save
            sleep(sleep_time)

    return find_elements_decorator
