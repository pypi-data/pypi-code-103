"""Dom elements."""

from typing import TYPE_CHECKING, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from sop import DEFAULT_TIMOUT_PAGE_LOAD
from sop.elements import ClickElement, Locator, TextToBeEqual
from sop.odoo.terms import get_term as _t

if TYPE_CHECKING:

    from sop.odoo import BasePage
    from sop.odoo.dialogs import BaseDialog
    from sop.odoo.views import BaseRow


class WaitingMixin:
    """Mixin in order to wait odoo async task"""

    def wait_loading(self, max_wait=0.5, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        """Wait the end of loading, there is an handy class o_wait on body
        while performing call to the server (retreive data).

        For instance while you clear all filters a new search is perform,
        if you click to quickly on filter menu before search was really loaded
        the dropdown menu is closed at the end. There is no easy way to ensure
        load is termitated in such case. Or while switching from one list
        view to an other.

        :param max_wait: maximum of delay to wait the oe_class it is possible
        that the class was removed before running this command it won't failed
        :param timeout: raise TimeoutException if oe_wait is still present after
        timeout s.

        This method is on BasePage (not on OdooBasePage) to be able to use it
        on Modal form.
        """
        try:
            WebDriverWait(self.driver, max_wait).until(
                lambda driver: driver.find_element_by_css_selector("body.oe_wait"),
                message=f"'body.oe_wait' not found in {max_wait}s.",
            )
        except TimeoutException:
            pass

        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "body.oe_wait")),
            message=f"'body.oe_wait' is still present after {timeout}s",
        )


class BaseOdooElement(WaitingMixin):
    """Provide common pattern to odoo components"""

    def __init__(self, locator: Locator, timeout: int = DEFAULT_TIMOUT_PAGE_LOAD):
        """
        locator: tuple (By.<kind_of_search>, <search value>)
        timeout: waiting time in second for the given element
        """
        self.locator = locator
        self.timeout = timeout

    def __get__(self, obj: "BasePage", owner):
        """return component, getting value must be implement in a property
        of the component as user should use like this `page.my_el.value`
        """
        if hasattr(obj, "parent_el"):
            # In case of M2O list in form view parent_el represent the list
            # this let search row element only in sub entries
            self.driver = obj.parent_el.el
        else:
            self.driver = obj.driver
        return self

    @property
    def el(self):
        WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(self.locator),
            message=f"could not found {self.locator} in {self.timeout}s",
        )
        return self.driver.find_element(*self.locator)

    def click(self, locator, timeout=None, msg=None, relative_locator=False):
        if not timeout:
            timeout = self.timeout
        if not msg:
            msg = f"Couldn't click on {locator} in given time {timeout}s"
        # some time odoo refresh screen because multiple call are done to
        # the backend (likes loading autocomplete partner) or similar things
        # ensure page is not loading before loading
        self.wait_loading()
        WebDriverWait(self.el if relative_locator else self.driver, timeout).until(
            ClickElement(locator), message=msg
        )

    def wait_child(self, locator, timeout=None):
        if not timeout:
            timeout = self.timeout

        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: self.el.find_element(*locator),
            message=f"could not found {locator} in {self.timeout}s",
        )
        return self.el.find_element(*locator)

    def has_class(self, name):
        return name in self.el.get_attribute("class")

    @property
    def is_required(self):
        return self.has_class("o_required_modifier")

    @property
    def is_readonly(self):
        return self.has_class("o_readonly_modifier")

    @property
    def value(self):
        return self.text

    @property
    def text(self):
        return self.el.text

    def assertTextEqual(self, expected_text: str, timeout=None):
        if not timeout:
            timeout = self.timeout
        WebDriverWait(self.driver, timeout).until(
            TextToBeEqual(self, expected_text),
            message=f"Expected text: '{expected_text}' do not match in the given time "
            f"{timeout}s. Current text {self.text}.",
        )


class Ribbon(BaseOdooElement):
    def __init__(
        self, locator: Locator = None, timeout: int = DEFAULT_TIMOUT_PAGE_LOAD
    ):
        if not locator:
            locator = (By.CSS_SELECTOR, "div.ribbon")
        super().__init__(locator, timeout=timeout)


class SearchInputBar(BaseOdooElement):
    def __set__(self, obj: "BasePage", value: str):
        """Sets the text to the value supplied"""
        self.el.send_keys(value)

    def enter(self):
        self.el.send_keys(Keys.ENTER)

    def click_item(self, entry, expand=False):
        locator = (
            By.XPATH,
            f"..//li[contains(@class, 'o_menu_item')]/a/em[text()='{entry}']"
            + ("../../a[@class='o_expand']" if expand else ""),
        )
        self.click(
            locator,
            relative_locator=True,
        )

    def remove_first_facet(self):
        """remove first facet found
        Do not remove all facet as we needs to wait page refresh
        between to removes, usage::

            while self.search_bar_el.remove_first_facet():
                self.wait_loading()
        """
        facets = self.el.find_elements_by_xpath(
            "(..//i[contains(@class, 'o_facet_remove')])[1]"
        )
        if facets:
            self.click(
                (By.XPATH, "(..//i[contains(@class, 'o_facet_remove')])[1]"),
                relative_locator=True,
            )
            return True
        return False


class DropDownElement(BaseOdooElement):
    def open(self):
        self.click(self.locator)

    def close(self):
        self.el.send_keys(Keys.ESCAPE)

    def ensure(self, name, selected=True, timeout=None):
        if not timeout:
            timeout = self.timeout
        item = self.wait_child(
            (
                By.XPATH,
                f"../ul/li[contains(@class, 'o_menu_item')]/a[contains(text(), '{name}')]",
            ),
        )
        if str2bool(item.get_attribute("aria-checked")) is not selected:
            item.click()


class InputElement(BaseOdooElement):
    """Text Input Element class."""

    def __init__(
        self,
        locator: Locator,
        timeout: int = DEFAULT_TIMOUT_PAGE_LOAD,
        send_backspace: bool = False,
    ):
        """
        locator: tuple (By.<kind_of_search>, <search value>)
        timeout: waiting time in second for the given element
        send_backspace: send backspace to clear previous value
        """
        self.locator = locator
        self.timeout = timeout
        self.send_backspace = send_backspace

    def __set__(self, obj: "BasePage", value: str):
        """Sets the text to the value supplied"""
        value = str(value)
        self.driver = obj.driver
        if self.send_backspace:
            # using input-number, while clearing set to 1 so value is add the
            # the first character, select all
            # wondering why this doesn't works on export-name element
            # from selenium.webdriver.common.action_chains import ActionChains
            # ActionChains(a_search.driver).key_down(Keys.CONTROL)
            # .send_keys("a").key_up(Keys.CONTROL).perform()
            for _ in range(0, len(self.value)):
                self.el.send_keys(Keys.BACKSPACE)
        else:
            self.el.clear()
        self.el.send_keys(value)

    @property
    def value(self):
        if self.is_readonly:
            return self.el.text
        else:
            return self.el.get_attribute("value")


class MonetaryElement(InputElement):
    def __init__(
        self,
        locator: Locator,
        timeout: int = DEFAULT_TIMOUT_PAGE_LOAD,
        send_backspace: bool = True,
    ):
        """change default value to send_backspace"""
        super().__init__(locator, timeout=timeout, send_backspace=send_backspace)

    @property
    def el(self):
        """Odoo Moneray Widget are wrapped in a div"""
        el = super().el
        return el.find_element_by_tag_name("input")


class SelectElement(InputElement):
    """Select form input Element class."""

    def __set__(self, obj: "BasePage", value: str):
        """Sets the text to the value supplied"""
        self.driver = obj.driver
        Select(self.el).select_by_visible_text(value)


class RadioElement(BaseOdooElement):
    """TODO: finalize and test:
    * both mode read/edit
    * text/value
    """

    def __init__(self, *args, horizontal=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontal = horizontal

    def __set__(self, obj: "BasePage", value: str):
        """Sets the text to the value supplied"""
        self.driver = obj.driver
        self.el.find_element_by_xpath(f"./div/input[@data-value='{value}']/..").click()

    def set_by_text(self, text: str):
        """Sets the text to the value supplied"""
        self.el.find_element_by_xpath(
            f"./div/label[contains(text(), '{text}')]"
        ).click()

    # @property
    # def value(self):
    #     """Gets if the input text is selected"""
    #     element = self.el.find_element_by_xpath("./div/input[checked='true']")
    #     return element.is_selected()


class CheckboxElement(BaseOdooElement):
    """CheckboxElement form input Element class."""

    def __set__(self, obj: "BasePage", checked: bool):
        """Click on the checkbox if necessary to obtain the desired state"""
        self.driver = obj.driver
        if self.value != checked:
            self.el.click()
            if self.value != checked:
                raise AssertionError(
                    f"Something goes wrong while trying to set ({checked}) the "
                    f"checkbox {self.locator[1]} got "
                    f"({self.__get__(obj, None)})"
                )

    @property
    def value(self):
        """Gets if the input text is selected"""
        element = self.el.find_element_by_tag_name("input")
        return element.is_selected()


class Many2One(BaseOdooElement):
    """Many2One field on form view"""

    def __init__(
        self,
        locator: Locator,
        timeout: int = DEFAULT_TIMOUT_PAGE_LOAD,
        dialog: "BaseDialog" = None,
        form_view: "BasePage" = None,
    ):
        """
        locator: tuple (By.<kind_of_search>, <search value>)
        timeout: waiting time in second for the given element
        dialog: dialog to open if create is selected
        form_view: Expected page Object (`BasePage`) which define the form view
                    used when clicking on an element.
        """
        self.locator = locator
        self.timeout = timeout
        self.dialog = dialog
        self.form_view = form_view

    def __set__(self, obj: "BasePage", value: Tuple[str, str]):
        """Find/create M2o providing a tuple (<search value>, <selected value>)"""
        self.driver = obj.driver
        self.click_item(value[0], entry=value[1])

    @property
    def el(self):
        """in edit mode we have to get the input child element"""
        WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(self.locator),
            message=".el could't be resolved because "
            f"could not found {self.locator} in {self.timeout}s",
        )
        el = self.driver.find_element(*self.locator)
        if "o_field_many2one" in el.get_attribute("class"):
            el = el.find_element(By.TAG_NAME, "input")
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of(el))
        return el

    def click_item(self, search, entry=None):
        if not entry:
            entry = search
        self.el.clear()
        self.el.send_keys(search)
        locator = (
            By.XPATH,
            f"//a[@class='ui-menu-item-wrapper' and contains(text(),'{ entry }')]"
            f"|//li[@class='ui-menu-item']/a[contains(text(),'{ entry }')]",
        )
        self.click(locator)
        # WebDriverWait(self.driver, self.timeout).until(
        #     lambda driver: driver.find_element(*locator),
        #     message=f"could not found {locator[1]} in {self.timeout}s",
        # )
        # element = self.driver.find_element(*locator)
        # ActionChains(element.parent).move_to_element(element).perform()
        # element.click()

    @property
    def value(self):
        # not tested
        return self.el.get_attribute("value")

    def create_and_update(self, new_name):
        self.click_item(new_name, entry=_t("Create and Edit..."))
        return self.dialog(self.driver)

    def go_to_form(self, timeout=None):
        if self.is_readonly:
            if not self.form_view:
                raise NotImplementedError(
                    "You must set `form_view` value a `BasePage` object"
                )
            self.click(self.locator, timeout=timeout)
            self.el.click()
            return self.form_view(self.driver)
        else:
            raise NotImplementedError(
                "You must leave edit mode or we expecte "
                "a readonly field, moving to the related object while "
                "editing is not implemented"
            )


class One2Many(BaseOdooElement):
    def __init__(
        self,
        locator: Locator,
        timeout: int = DEFAULT_TIMOUT_PAGE_LOAD,
        row_view: "BaseRow" = None,
        dialog: "BaseDialog" = None,
    ):
        """
        locator: tuple (By.<kind_of_search>, <search value>) to get M2o in a form view
        timeout: waiting time in second for the given element
        row_view: Expected page Object (`BaseRow`) which define editable fields on
                  M2O model.
        dialog: if set editing the row open a dialog
        """
        self.locator = locator
        self.timeout = timeout
        self.row_view = row_view
        self.dialog = dialog

    def new(self):
        """Click on the add new button
        wait new line creation and return row object instance
        """
        self.click(
            (By.CSS_SELECTOR, "tr > td.o_field_x2many_list_row_add > a:nth-child(1)"),
            relative_locator=True,
        )
        if self.dialog:
            return self.dialog(self.driver)
        else:
            return self.row_view(self.driver, self)


class StatusBarElement(BaseOdooElement):
    @property
    def buttons(self):
        return self.el.find_elements_by_tag_name("button")

    @property
    def displayed_values(self):
        return [button.get_attribute("data-value") for button in self.buttons]

    @property
    def value(self):
        for button in self.buttons:
            if str2bool(button.get_attribute("aria-checked")):
                return button.get_attribute("data-value")
        raise ValueError("There is no status defined.")

    @property
    def text(self):
        for button in self.buttons:
            if str2bool(button.get_attribute("aria-checked")):
                return button.text
        return ""

    def assertStateEqual(self, expected_text: str, timeout=None):
        if not timeout:
            timeout = self.timeout
        WebDriverWait(self.driver, timeout).until(
            TextToBeEqual(self, expected_text, property_attr="value")
        )


def str2bool(s):
    return s.lower() in ["y", "yes", "1", "true", "t", "on"]
