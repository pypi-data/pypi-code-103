from . import decorators
from .helpers import validate_time_settings
from selenium.webdriver.common.by import By


class WebDriverMixin:
    """
    Enhances the selenium.webdriver.remote.webdriver.WebDriver
    with several enhanced capabilities.
    """

    def __init__(self, *args, **kwargs):
        self._timeout = kwargs.get("timeout", 0)
        self._poll_frequency = kwargs.get("poll_frequency", 0.5)
        self._recover = kwargs.get("recover", None)
        self._debounce = kwargs.get("debounce", 0.0)
        self._implicitly_wait = kwargs.get("implicitly_wait", 0.0)
        validate_time_settings(
            self._implicitly_wait, self._timeout, self._poll_frequency
        )
        delete = ("timeout", "poll_frequency", "recover", "debounce")
        kwargs = {k: v for (k, v) in kwargs.items() if k not in delete}
        super().__init__(*args, **kwargs)

    def implicitly_wait(self, time_to_wait):
        """
        Sets a sticky timeout to implicitly wait for an element to be found,
           or a command to complete. This method only needs to be called one
           time per session. To set the timeout for calls to
           execute_async_script, see set_script_timeout.

        Warning: The selenious package will fail if implicitly_wait is larger
        than timeout or poll_frequency.  It is better to not set this and
        instead use the timeout property.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            driver.implicitly_wait(30)
        """
        validate_time_settings(time_to_wait, self.timeout, self.poll_frequency)

        self._implicitly_wait = time_to_wait
        return super().implicitly_wait(time_to_wait)

    @property
    def timeout(self):
        """The default selenious timout.

        The selenium webdriver has an implicitly_wait() command that
        once set cannot be overwritten.  There is also a WebDriverWait()
        facility to allow requests with a wait.  This command moves
        an equivalent to that capability directly into the select commands.
        You can specify a global wait timeout with timeout property or pass
        a timeout parameter directly to the select command.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        validate_time_settings(self._implicitly_wait, timeout, self._poll_frequency)
        self._timeout = timeout

    @property
    def debounce(self):
        """The wait time for a select to have not changed."""
        return self._debounce

    @debounce.setter
    def debounce(self, debounce):
        self._debounce = debounce

    @property
    def poll_frequency(self):
        """The frequency polling will happen for the timeout.

        This is similar to the WebDriverWait polling frequency.  See
        set_timeout() for differences.
        """

        return self._poll_frequency

    @poll_frequency.setter
    def poll_frequency(self, poll_frequency):
        validate_time_settings(self._implicitly_wait, self.timeout, poll_frequency)

        self._poll_frequency = poll_frequency

    @property
    def recover(self):
        """The recover function.

        The recover function is run when a select fails or some
        actions like click fail.  The intent is to try to fix
        expected, but not typical web activities like an advertising
        popup covering the page being manipulated.

        The recovery function is guaranteed to be run at least once
        if there is an issue, but may be run multiple times at the
        poll_frequency if there is a timeout.

        :Args:
        - recover - The recover function to be run.  Parameters are:
          - webdriver - This webdriver (self)
          - function - The function calling the recover function.
          - kwargs - The kwargs sent to the function
          - elapsed - The time elapsed since the first attempt.
          - attempts - The number of attempts
        """
        return self._recover

    @recover.setter
    def recover(self, recover):
        self._recover = recover

    @decorators.find_element
    def find_element(
        self, by=By.ID, value=None, timeout=None, poll_frequency=None, recover=None
    ):
        """
        Finds an element by selenium.webdriver.common.by and value.
        :Args:
         - by - One of By.ID (default), By.XPATH, By.LINK_TEXT, By.PARTIAL_LINK_TEXT,
                   By.NAME, By.TAG_NAME, By.CLASS_NAME, By.CSS_SELECTOR
         - value - The value to search for.
         - timeout - The timeout to wait for element.
           Default is WebDriverMixin.timeout (0.0)
         - poll_frequency - How often to poll Selenious for the element if there is a timeout.
           Default is WebDriverMixin.poll_frequency (0.5)
         - recover - A function called after each poll (but not the last)
           Default is WebDriverMixin.recover (None)
        :Returns:
         - SeleniousWebElement - the element if it was found
        :Raises:
         - NoSuchElementException - if the element wasn't found
        :Usage:
            ::
                element = driver.find_element(By.ID, 'foo')
        """
        return super().find_element(by=by, value=value)

    @decorators.find_elements
    def find_elements(
        self,
        by=By.ID,
        value=None,
        timeout=None,
        poll_frequency=None,
        recover=None,
        min=None,
        debounce=None,
    ):
        """
        Finds multiple elements by selenium.webdriver.common.by and value.
        :Args:
         - by - One of By.ID (default), By.XPATH, By.LINK_TEXT, By.PARTIAL_LINK_TEXT,
           By.NAME, By.TAG_NAME, By.CLASS_NAME, By.CSS_SELECTOR
         - value - The value to search for.
         - timeout - The timeout to wait for min elements.  Default is WebDriverMixin.timeout (0)
         - poll_frequency - How often to poll Selenious for the element if there
           is a timeout.  Default is WebDriverMixin.poll_frequency (0.5)
         - recover - A function called after each poll (but not the last)
           Default is WebDriverMixin.recover (None)        :Returns:
         - list of SeleniousWebElement - the element if it was found. An
           empty list if not
         - min - The minimum number of elements to wait for.  Default is 0.
         - debounce - A time to wait for the number of elements to not change.
           Default is WebDriverMixin.debounce (0.0)
        :Usage:
            ::
                elements = driver.find_elements(By.ID, 'foo')
        """
        return super().find_elements(by=by, value=value)

    def find_element_by_id(self, id_, **kwargs):
        """
        Calls find_element(By.ID, value=id_, **kwargs)
        """
        return self.find_element(By.ID, value=id_, **kwargs)

    def find_elements_by_id(self, id_, **kwargs):
        """
        calls find_elements(By.ID, id_, **kwargs)
        """
        return self.find_elements(By.ID, id_, **kwargs)

    def find_element_by_xpath(self, xpath, **kwargs):
        """
        Calls find_element(By.XPATH, xpath, **kwargs)
        """
        return self.find_element(By.XPATH, xpath, **kwargs)

    def find_elements_by_xpath(self, xpath, **kwargs):
        """
        calls find_elements(By.XPATH, xpath, **kwargs)
        """
        return self.find_elements(By.XPATH, xpath, **kwargs)

    def find_element_by_link_text(self, link_text, **kwargs):
        """
        Calls find_element(By.LINK_TEXT, link_text, **kwargs)
        """
        return self.find_element(By.LINK_TEXT, link_text, **kwargs)

    def find_elements_by_link_text(self, link_text, **kwargs):
        """
        Calls find_elements(By.LINK_TEXT, link_text, **kwargs)
        """
        return self.find_elements(By.LINK_TEXT, link_text, **kwargs)

    def find_element_by_partial_link_text(self, partial_link_text, **kwargs):
        """
        calls find_element(By.PARTIAL_LINK_TEXT, partial_link_text, **kwargs)
        """
        return self.find_element(By.PARTIAL_LINK_TEXT, partial_link_text, **kwargs)

    def find_elements_by_partial_link_text(self, partial_link_text, **kwargs):
        """
        calls find_elements(By.PARTIAL_LINK_TEXT, partial_link_text, **kwargs)
        """
        return self.find_elements(By.PARTIAL_LINK_TEXT, partial_link_text, **kwargs)

    def find_element_by_name(self, name, **kwargs):
        """
        Calls find_element(By.NAME, name, **kwargs)
        """
        return self.find_element(By.NAME, name, **kwargs)

    def find_elements_by_name(self, name, **kwargs):
        """
        calls find_elements(By.NAME, name, **kwargs)
        """
        return self.find_elements(By.NAME, name, **kwargs)

    def find_element_by_tag_name(self, tag_name, **kwargs):
        """
        Calls find_element(By.TAG_NAME, tag_name, **kwargs)
        """
        return self.find_element(By.TAG_NAME, tag_name, **kwargs)

    def find_elements_by_tag_name(self, tag_name, **kwargs):
        """
        calls find_elements(By.TAG_NAME, tag_name, **kwargs)
        """
        return self.find_elements(By.TAG_NAME, tag_name, **kwargs)

    def find_element_by_class_name(self, class_name, **kwargs):
        """
        Calls find_element(By.CLASS_NAME, class_name, **kwargs)
        """
        return self.find_element(By.CLASS_NAME, class_name, **kwargs)

    def find_elements_by_class_name(self, class_name, **kwargs):
        """
        calls find_elements(By.CLASS_NAME, class_name, **kwargs)
        """
        return self.find_elements(By.CLASS_NAME, class_name, **kwargs)

    def find_element_by_css_selector(self, css_selector, **kwargs):
        """
        Calls find_element(By.CSS_SELECTOR, css_selector, **kwargs)
        """
        return self.find_element(By.CSS_SELECTOR, css_selector, **kwargs)

    def find_elements_by_css_selector(self, css_selector, **kwargs):
        """
        calls find_elements(By.CSS_SELECTOR, css_selector, **kwargs)
        """
        return self.find_elements(By.CSS_SELECTOR, css_selector, **kwargs)
