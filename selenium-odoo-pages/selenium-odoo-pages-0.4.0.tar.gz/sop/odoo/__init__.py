"""Odoo base pages following selenium
`page objects pattern
<https://selenium-python.readthedocs.io/page-objects.html>`_
recommandations.
"""
from typing import TYPE_CHECKING, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sop import DEFAULT_TIMOUT_ACTION, DEFAULT_TIMOUT_PAGE_LOAD
from sop.elements import expected_number_tabs
from sop.odoo.elements import ClickElement, InputElement, WaitingMixin

Locator = Tuple[str, str]

if TYPE_CHECKING:
    from sop.odoo.accounting import BaseAccountingPage, InvoiceListViewPage
    from sop.odoo.elements import BaseOdooElement
    from sop.odoo.sales import (
        BaseSalesPage,
        ProductTemplateListViewPage,
        SaleOrderListViewPage,
    )


class BasePage(WaitingMixin):
    """Base class to initialize the base page that will be called from all pages"""

    _page_selector: Optional[Locator] = None

    def __init__(self, driver: webdriver, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        self.driver = driver
        if self._page_selector:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._page_selector),
                message=f"Couldn't find ({self._page_selector[0]}, "
                f"{self._page_selector[1]}) in {timeout}s",
            )

    def click(self, by_locator: Locator, timeout: int = DEFAULT_TIMOUT_PAGE_LOAD):
        """Wait for the element to be clickable, then click.

        First we wait for an eventual loading overlay to disappear then we check if the
        element is visible & active before clicking it.
        """
        WebDriverWait(self.driver, timeout).until(
            ClickElement(by_locator),
            message=f"Couldn't click on {by_locator} in given time {timeout}s",
        )

    def assert_open_tabs(self, number, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        WebDriverWait(self.driver, timeout).until(
            expected_number_tabs(number),
            message=f"Expected {number} tabs open in given time {timeout}s",
        )


class OdooNavbarLocators:
    PAGE_SELECTOR = (By.CSS_SELECTOR, 'nav[class="o_main_navbar"]')
    MAIN_MENU_APPS = (By.CSS_SELECTOR, 'ul[class="o_menu_apps"] > li > a')
    MENU_APP_SALES = (By.CSS_SELECTOR, 'a[data-menu-xmlid="sale.sale_menu_root"]')
    MENU_APP_FINANCE = (By.CSS_SELECTOR, 'a[data-menu-xmlid="sale.menu_finance"]')

    MAIN_MENU_USER = (
        By.CSS_SELECTOR,
        'ul[class="o_menu_systray"] > li[class="o_user_menu"] > a',
    )
    MENU_DISCONNECT = (By.CSS_SELECTOR, 'a[data-menu="logout"]')


class OdooBasePage(BasePage):
    """Navbar behaviours"""

    _page_selector = OdooNavbarLocators.PAGE_SELECTOR

    def __init__(self, driver: webdriver, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        super().__init__(driver, timeout=timeout)
        self.wait_loading(timeout=timeout)

    def click_menu_sales_app(self) -> "BaseSalesPage":
        from sop.odoo.sales import BaseSalesPage

        self.click(OdooNavbarLocators.MAIN_MENU_APPS)
        self.click(OdooNavbarLocators.MENU_APP_SALES)
        return BaseSalesPage(self.driver)

    def click_menu_quotations(self) -> "SaleOrderListViewPage":
        return self.click_menu_sales_app().click_menu_quotations()

    def click_menu_sale_order(self) -> "SaleOrderListViewPage":
        return self.click_menu_sales_app().click_menu_sale_order()

    def click_menu_product_template(self) -> "ProductTemplateListViewPage":
        return self.click_menu_sales_app().click_menu_product_template()

    def click_menu_accounting_app(self) -> "BaseAccountingPage":
        from sop.odoo.accounting import BaseAccountingPage

        self.click(OdooNavbarLocators.MAIN_MENU_APPS)
        self.click(OdooNavbarLocators.MENU_APP_FINANCE)
        return BaseAccountingPage(self.driver)

    def click_menu_invoice(self) -> "InvoiceListViewPage":
        return self.click_menu_accounting_app().click_menu_invoice()

    def disconnect(self, timeout=DEFAULT_TIMOUT_PAGE_LOAD) -> "OdooLoginPage":
        self.click(OdooNavbarLocators.MAIN_MENU_USER)
        self.click(OdooNavbarLocators.MENU_DISCONNECT)
        self.wait_loading(timeout=timeout)
        return OdooLoginPage(self.driver, timeout=timeout)


class OdooLoginPageLocators:

    PAGE_SELECTOR = (By.CSS_SELECTOR, 'form[class="oe_login_form"]')
    LOGIN = (By.ID, "login")
    PASSWORD = (By.ID, "password")
    PASSWORD = (By.ID, "password")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")


class OdooLoginPage(BasePage):
    """Login page as no navbar directly inherit from BasePage"""

    _page_selector = OdooLoginPageLocators.PAGE_SELECTOR

    login_el = InputElement(OdooLoginPageLocators.LOGIN)
    password_el = InputElement(OdooLoginPageLocators.PASSWORD)

    def connect(self) -> "OdooBasePage":
        self.click(OdooLoginPageLocators.SUBMIT_BUTTON)
        return OdooBasePage(self.driver)


def odoo_authentication(frontend, login, password):
    """Disconnect existing session if any and try to
    authenticat new user for given login, password"""
    try:
        # first try to disconnect (failed fast)
        page = OdooBasePage(frontend, timeout=1)
        # if we get the page we use a bigger timeout to
        # instantiate the new page
        login_page = page.disconnect(timeout=DEFAULT_TIMOUT_ACTION)
    except TimeoutException:
        # gives more time to disconenct ?
        login_page = OdooLoginPage(frontend, timeout=DEFAULT_TIMOUT_ACTION)

    login_page.login_el = login
    login_page.password_el = password
    return login_page.connect()


class BaseRowLocator:
    PAGE_SELECTOR = (By.CSS_SELECTOR, "tr.o_selected_row")


class BaseRow(BasePage):
    """Base row for O2M fields in form view edition"""

    _page_selector = BaseRowLocator.PAGE_SELECTOR

    def __init__(
        self,
        driver: webdriver,
        parent_element: "BaseOdooElement",
        timeout=DEFAULT_TIMOUT_PAGE_LOAD,
    ):
        super().__init__(driver, timeout=timeout)
        self.parent_el = parent_element
