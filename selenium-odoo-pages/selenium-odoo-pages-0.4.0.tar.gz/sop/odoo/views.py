from selenium.webdriver.common.by import By

from sop import DEFAULT_TIMOUT_PAGE_LOAD
from sop.odoo.elements import DropDownElement, InputElement, Ribbon, SearchInputBar


class SearchViewMixinLocators:
    """locators related to the search odoo view"""

    FILTER_MENU = (By.CSS_SELECTOR, "div.o_filter_menu > button")
    SEARCH_BAR = (By.CSS_SELECTOR, "input.o_searchview_input")
    FACETTE_REMOVE = (By.CSS_SELECTOR, "i.o_facet_remove")


class SearchViewMixin:
    """Mixin to manage search view


    page.defined_filter("A valider", enable=True)
    page.add_filter("Something to search as default ")
    page.add_filter("expected search", element="what", expected_value="expected search select value")
    """

    search_bar_el = SearchInputBar(SearchViewMixinLocators.SEARCH_BAR)
    search_menu_el = DropDownElement(SearchViewMixinLocators.FILTER_MENU)

    def defined_filter(self, filter_name: str, selected=True):
        self.search_menu_el.open()
        self.search_menu_el.ensure(filter_name, selected=selected)
        self.wait_loading()
        self.search_menu_el.close()

    def add_filter(self, search_pattern, element=None, expected_value=None):
        """Add filter using auto completion

        search_pattern: the value to search typed by the user
        element: element used for autocompletion or direct search
        expected_value: search value in case of element is autocompleted fields
          require element params
        """
        if expected_value and not element:
            raise ValueError(
                f"element parameter is mandatory while providing expected_value: {expected_value}."
                "element is used to choose from which field you want auto-completion"
            )
        self.search_bar_el = search_pattern
        if element is not None:
            self.wait_loading()
            self.search_bar_el.click_item(element, expand=bool(expected_value))
            if expected_value:
                self.wait_loading()
                self.search_bar_el.click_item(expected_value)
        else:
            self.search_bar_el.enter()
        self.wait_loading()

    def clear_filters(self):
        while self.search_bar_el.remove_first_facet():
            self.wait_loading()


class FormViewMixinLocators:
    CREATE_BUTTON = (By.CSS_SELECTOR, "button.o_form_button_create")
    SAVE_BUTTON = (
        By.CSS_SELECTOR,
        "button.o_form_button_save, button.o_list_button_save",
    )
    EDIT_BUTTON = (By.CSS_SELECTOR, "button.o_form_button_edit")

    TAB_TEMPLATE = (
        By.XPATH,
        "//div[@class='o_notebook_headers']/ul/li/a[contains(text(), '{tab_name}')]",
    )
    STAT_BUTTON = (
        By.XPATH,
        "//button[@class='btn oe_stat_button'][@name='{action_name}']",
    )


class FormViewMixin:
    ribbon_el = Ribbon()

    def click_create(self):
        self.click(FormViewMixinLocators.CREATE_BUTTON)

    def click_edit(self):
        self.click(FormViewMixinLocators.EDIT_BUTTON)

    def click_save(self):
        self.click(FormViewMixinLocators.SAVE_BUTTON)

    def switch_tab(self, name):
        self.click(
            (
                FormViewMixinLocators.TAB_TEMPLATE[0],
                FormViewMixinLocators.TAB_TEMPLATE[1].format(tab_name=name),
            )
        )

    def click_stat_button(self, action_name):
        self.click(
            (
                FormViewMixinLocators.STAT_BUTTON[0],
                FormViewMixinLocators.STAT_BUTTON[1].format(action_name=action_name),
            )
        )


class ListViewMixinLocators:
    ADD_BUTTON = (By.CSS_SELECTOR, "button.o_list_button_add")
    CELL_BY_TEXT = (
        By.XPATH,
        "//table[contains(@class, 'o_list_table')]/tbody/tr/td[contains(text(), '{value}')]",
    )
    PAGER_TOTAL = (
        By.XPATH,
        "//span[contains(@class, 'o_pager_limit')]",
    )


class ListViewMixin(SearchViewMixin):
    pager_total = InputElement(ListViewMixinLocators.PAGER_TOTAL)

    def click_create(self):
        self.click(ListViewMixinLocators.ADD_BUTTON)
        return self._form_view(self.driver)

    def open_form_view(self, value, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        locator = (
            ListViewMixinLocators.CELL_BY_TEXT[0],
            ListViewMixinLocators.CELL_BY_TEXT[1].format(value=value),
        )
        self.click(locator, timeout=timeout)
        return self._form_view(self.driver, timeout=timeout)

    @property
    def total_record(self):
        return int(self.pager_total.text)


class KanbanViewMixinLocators:
    ADD_BUTTON = (By.CSS_SELECTOR, "button.o-kanban-button-new")


class KanbanViewMixin(SearchViewMixin):
    def click_create(self):
        self.click(KanbanViewMixinLocators.ADD_BUTTON)
        return self._form_view(self.driver)
