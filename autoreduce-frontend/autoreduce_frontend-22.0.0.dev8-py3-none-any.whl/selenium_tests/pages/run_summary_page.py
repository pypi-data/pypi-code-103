# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Module for the run summary page model."""
from functools import partial
from typing import List

from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.rerun_form_mixin import RerunFormMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.tour_mixin import TourMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class RunSummaryPage(Page, RerunFormMixin, NavbarMixin, FooterMixin, TourMixin):
    """Page model class for run summary page."""
    def __init__(self, driver, instrument, run_number, version, batch_run=False):
        super().__init__(driver)
        self.instrument = instrument
        self.run_number = run_number
        self.version = version
        self.batch_run = batch_run

    def url_path(self) -> str:
        """Return the current URL of the page."""
        if not self.batch_run:
            return reverse("runs:summary",
                           kwargs={
                               "instrument_name": self.instrument,
                               "run_number": self.run_number,
                               "run_version": self.version
                           })
        else:
            return reverse("runs:batch_summary",
                           kwargs={
                               "instrument_name": self.instrument,
                               "pk": self.run_number,
                               "run_version": self.version
                           })

    @property
    def reduction_job_panel(self) -> WebElement:
        """Return the run summary panel."""
        return self.driver.find_element_by_id("reduction_job_panel")

    @property
    def rerun_form(self) -> WebElement:
        """Return the rerun form."""
        return self.driver.find_element_by_id("rerun_form")

    @property
    def toggle_button(self) -> WebElement:
        """Return the toggle button."""
        return self.driver.find_element_by_id("toggle_form")

    @property
    def reset_to_initial_values(self) -> WebElement:
        """Return the `Reset to original script and values` button."""
        return self.driver.find_element_by_id("resetValues")

    @property
    def reset_to_current_values(self) -> WebElement:
        """
        Return the `Reset to values in the current reduce_vars script` button.
        """
        return self.driver.find_element_by_id("currentScript")

    @property
    def warning_message(self) -> WebElement:
        """Return the 'warning_message' box."""
        return self.driver.find_element_by_id("warning_message")

    @property
    def next_run_button(self) -> WebElement:
        """Return the button for returning the next run."""
        return self.driver.find_element_by_id("next")

    @property
    def previous_run_button(self) -> WebElement:
        """Return the button for returning the previous run."""
        return self.driver.find_element_by_id("previous")

    @property
    def toggle_data_path_button(self) -> WebElement:
        """Return the toggle button for toggling the form on the page."""
        return self.driver.find_element_by_id("datapath_toggle")

    def run_description_text(self) -> str:
        """Return the text of the 'run_description' field."""
        return self.driver.find_element_by_id("run_description").text

    def title_text(self) -> str:
        """Return the text of the title field."""
        return self.driver.find_element_by_id("runTitle").text

    def started_by_text(self) -> str:
        """Return the text of the 'started_by' field."""
        return self.driver.find_element_by_id("started_by").text

    def status_text(self) -> str:
        """Return the text of the 'status' field."""
        return self.driver.find_element_by_id("status").text

    def instrument_text(self) -> str:
        """Return the text of the 'instrument' field."""
        return self.driver.find_element_by_id("instrument").text

    def rb_number_text(self) -> str:
        """Return the text of the 'rb_number' field."""
        return self.driver.find_element_by_id("rb_number").text

    def last_updated_text(self) -> str:
        """Return the text of the 'last_updated' field."""
        return self.driver.find_element_by_id("last_updated").text

    def data_path_text(self) -> str:
        """Return the text of the data location field."""
        return self.driver.find_element_by_class_name("file-path").text

    def reduction_host_text(self) -> WebElement:
        """Return the text of the 'reduction_host' field."""
        return self.driver.find_element_by_id("reduction_host").text

    def images(self) -> List[WebElement]:
        """Returns all image elements."""
        return self.driver.find_elements_by_tag_name("img")

    def plotly_plots(self) -> List[WebElement]:
        """Return all plotly plot elements."""
        return self.driver.find_elements_by_class_name("js-plotly-plot")

    def _do_cancel_btn(self, url):
        def run_button_clicked_successfully(button, url, driver):
            button.click()
            return driver.current_url.split("?")[0].endswith(url)

        button = self.driver.find_element_by_id("cancel")
        WebDriverWait(self.driver, 10).until(partial(run_button_clicked_successfully, button, url))

    def click_cancel_btn(self):
        """Click the cancel button and return a RunsListPage object."""
        # pylint:disable=cyclic-import,import-outside-toplevel
        from autoreduce_frontend.selenium_tests.pages.runs_list_page import RunsListPage

        self._do_cancel_btn(reverse("runs:list", kwargs={"instrument": self.instrument}))
        return RunsListPage(self.driver, self.instrument)

    def click_btn_by_id(self, btn_id: str) -> None:
        """Click the button with the given id."""
        btn = self.driver.find_element_by_id(btn_id)
        btn.click()

    def is_disabled(self, element_id):
        """Return True if the element with the given id is disabled, otherwise, False."""
        return "disabled" in self.driver.find_element_by_id(element_id).get_attribute("class")
