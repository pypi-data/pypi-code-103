# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Module for the experiment summary page model."""
from typing import List

from django.urls.base import reverse
from selenium.webdriver.remote.webelement import WebElement

from autoreduce_frontend.selenium_tests.pages.component_mixins.footer_mixin import FooterMixin
from autoreduce_frontend.selenium_tests.pages.component_mixins.navbar_mixin import NavbarMixin
from autoreduce_frontend.selenium_tests.pages.page import Page


class ExperimentSummaryPage(Page, NavbarMixin, FooterMixin):
    """Page model class for experiment summary page."""
    def __init__(self, driver, reference_number):
        super().__init__(driver)
        self.reference_number = reference_number

    def url_path(self) -> str:
        """Return the current URL of the page."""
        return reverse("experiment_summary", kwargs={
            "reference_number": self.reference_number,
        })

    @property
    def reduction_job_panel(self) -> WebElement:
        """Return the experiment summary panel."""
        return self.driver.find_element_by_class_name("experiment_panel")

    def get_run_numbers_from_table(self) -> List[str]:
        """
        Return the list of run numbers visible on the current table of the
        experiment summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements_by_class_name("run-num-links")]

    def get_created_from_table(self) -> List[str]:
        """
        Return the list of created dates visible on the current table of the
        experiment summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements_by_class_name("last-updated-dates")]

    def get_status_from_table(self) -> List[str]:
        """
        Return the list of status visible on the current table of the
        experiment summary page.
        """
        return [run.text.split(" - ")[0] for run in self.driver.find_elements_by_class_name("run-status")]
