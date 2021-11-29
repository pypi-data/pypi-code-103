from selenium.webdriver.common.by import By

from sop import DEFAULT_TIMOUT_ACTION, DEFAULT_TIMOUT_PAGE_LOAD
from sop.odoo import BasePage
from sop.odoo.elements import CheckboxElement, InputElement, Many2One, RadioElement


class BaseDialogLocator:
    CLOSE = (
        By.XPATH,
        "//header[contains(@class, 'modal-header')]/button[contains(@class, 'close')]",
    )


class BaseDialog(BasePage):
    def close(self, timeout=DEFAULT_TIMOUT_PAGE_LOAD):
        self.click(BaseDialogLocator.CLOSE, timeout=timeout)


class PartnerDialogFormLocators:

    NAME = (
        By.NAME,
        "name",
    )
    EMAIL = (
        By.NAME,
        "email",
    )
    PHONE = (
        By.NAME,
        "phone",
    )
    STREET = (
        By.NAME,
        "street",
    )
    CITY = (
        By.NAME,
        "city_id",
    )
    COUNTRY = (
        By.NAME,
        "country_id",
    )
    SAVE_BUTTON = (
        By.CSS_SELECTOR,
        "div.modal-content footer.modal-footer button.btn.btn-primary",
    )


class PartnerDialogForm(BaseDialog):

    name_el = InputElement(PartnerDialogFormLocators.NAME)
    email_el = InputElement(PartnerDialogFormLocators.EMAIL)
    phone_el = InputElement(PartnerDialogFormLocators.PHONE)
    street_el = InputElement(PartnerDialogFormLocators.STREET)
    city_el = Many2One(PartnerDialogFormLocators.CITY)
    country_el = Many2One(
        PartnerDialogFormLocators.COUNTRY, timeout=DEFAULT_TIMOUT_ACTION
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # force France country
        self.country_el = ("Fr", "France")

    def save(self):
        self.click(PartnerDialogFormLocators.SAVE_BUTTON, timeout=DEFAULT_TIMOUT_ACTION)


class MailComposeFormLocators:
    SEND_BUTTON = (
        By.NAME,
        "action_send_mail",
    )


class MailComposeForm(BaseDialog):
    def mail_compose_send_message(self, timeout=DEFAULT_TIMOUT_ACTION):
        self.click(MailComposeFormLocators.SEND_BUTTON, timeout=timeout)


class InvoiceOrderWizardFormLocators:
    CREATE_AND_VIEW_BUTTON = (By.ID, "create_invoice_open")
    CREATE_BUTTON = (By.ID, "create_invoice")
    DEDUCT_DOWN_PAYMENTS = (By.NAME, "deduct_down_payments")
    METHOD = (By.NAME, "advance_payment_method")
    PERCENT_AMOUNT = (By.NAME, "amount")
    FIXED_AMOUNT = (By.NAME, "fixed_amount")


class InvoiceOrderWizardForm(BaseDialog):
    """Dialog to create invoice from Sale Order"""

    method_el = RadioElement(InvoiceOrderWizardFormLocators.METHOD)
    """delivered / percentage / fixed"""

    percentage_amount_el = InputElement(InvoiceOrderWizardFormLocators.PERCENT_AMOUNT)
    fixed_amount_el = InputElement(InvoiceOrderWizardFormLocators.FIXED_AMOUNT)
    deduct_down_payments_el = CheckboxElement(
        InvoiceOrderWizardFormLocators.DEDUCT_DOWN_PAYMENTS
    )

    def create_and_open_invoice(self, timeout=DEFAULT_TIMOUT_ACTION):
        from sop.odoo.accounting import InvoiceFormViewPage

        self.click(
            InvoiceOrderWizardFormLocators.CREATE_AND_VIEW_BUTTON, timeout=timeout
        )
        self.wait_loading(timeout=timeout)
        return InvoiceFormViewPage(self.driver, timeout=timeout)

    def create_invoice(self, timeout=DEFAULT_TIMOUT_ACTION):
        self.click(InvoiceOrderWizardFormLocators.CREATE_BUTTON, timeout=timeout)


class RegisterPayementWizardFormLocators:
    CREATE_BUTTON = (By.NAME, "action_create_payments")


class RegisterPayementWizardForm(BaseDialog):
    def create_payment(self):
        self.click(RegisterPayementWizardFormLocators.CREATE_BUTTON)
