from selenium.webdriver.common.by import By

from sop import DEFAULT_TIMOUT_ACTION
from sop.odoo import BaseRow, OdooBasePage
from sop.odoo.dialogs import InvoiceOrderWizardForm, MailComposeForm, PartnerDialogForm
from sop.odoo.elements import (
    InputElement,
    Many2One,
    One2Many,
    SelectElement,
    StatusBarElement,
)
from sop.odoo.terms import get_term as _t
from sop.odoo.views import FormViewMixin, KanbanViewMixin, ListViewMixin


class BaseSalesPageLocators:
    PAGE_SELECTOR = (By.XPATH, f"//nav//a[contains(text(), {_t('Sales')})]")

    MAIN_MENU_SALES = (By.CSS_SELECTOR, "a[data-menu-xmlid='sale.sale_order_menu']")
    MENU_QUOTATION = (By.CSS_SELECTOR, "a[data-menu-xmlid='sale.menu_sale_quotations']")
    MENU_SALE_ORDER = (By.CSS_SELECTOR, "a[data-menu-xmlid='sale.menu_sale_order']")
    MAIN_MENU_PRODUCTS = (
        By.CSS_SELECTOR,
        "a[data-menu-xmlid='sale.product_menu_catalog']",
    )
    MENU_PRODUCT_TEMPLATE = (
        By.CSS_SELECTOR,
        "a[data-menu-xmlid='sale.menu_product_template_action']",
    )


class BaseSalesPage(OdooBasePage):
    _page_selector = BaseSalesPageLocators.PAGE_SELECTOR

    def click_menu_quotations(self) -> "SaleOrderListViewPage":
        """Overwrite OdooBasePage"""
        self.click(BaseSalesPageLocators.MAIN_MENU_SALES)
        self.click(BaseSalesPageLocators.MENU_QUOTATION)
        return SaleOrderListViewPage(self.driver)

    def click_menu_sale_order(self) -> "SaleOrderListViewPage":
        """Overwrite OdooBasePage"""
        self.click(BaseSalesPageLocators.MAIN_MENU_SALES)
        self.click(BaseSalesPageLocators.MENU_SALE_ORDER)
        return SaleOrderListViewPage(self.driver)

    def click_menu_product_template(self) -> "ProductTemplateListViewPage":
        self.click(BaseSalesPageLocators.MAIN_MENU_PRODUCTS)
        self.click(BaseSalesPageLocators.MENU_PRODUCT_TEMPLATE)
        return ProductTemplateKanbanViewPage(self.driver)


class SaleOrderLineRowViewLocator:

    PRODUCT = (By.NAME, "product_id")
    QUANTITY = (By.NAME, "product_uom_qty")


class SaleOrderLineRowView(BaseRow):
    product_el = Many2One(SaleOrderLineRowViewLocator.PRODUCT)
    quantity_el = InputElement(
        SaleOrderLineRowViewLocator.QUANTITY, send_backspace=True
    )


class SaleOrderFormViewPageLocators:
    STATE = (By.NAME, "state")
    PAGE_SELECTOR = (By.CSS_SELECTOR, "div.o_form_view")
    QUOTATION_SEND = (By.NAME, "action_quotation_send")
    PRIMARY_CONFIRM = (By.CSS_SELECTOR, "button.btn-primary[name='action_confirm']")
    SECONDARY_CONFIRM = (By.CSS_SELECTOR, "button.btn-secondary[name='action_confirm']")
    CREATE_INVOICE = (
        By.XPATH,
        "//div[contains(@class, 'o_statusbar_buttons')]"
        "/button[not(contains(@class, 'o_invisible_modifier'))]"
        "/span[contains(text(), '"
        f"{_t('Create Invoice')}')]",
    )
    PRICELIST = (By.NAME, "pricelist_id")
    PARTNER = (By.NAME, "partner_id")
    ORDER_LINE = (By.NAME, "order_line")
    INVOICE_STATUS = (By.NAME, "invoice_status")


class SaleOrderFormViewPage(BaseSalesPage, MailComposeForm, FormViewMixin):
    _page_selector = SaleOrderFormViewPageLocators.PAGE_SELECTOR
    state_el = StatusBarElement(SaleOrderFormViewPageLocators.STATE)
    pricelist_el = SelectElement(SaleOrderFormViewPageLocators.PRICELIST)
    invoice_status_el = SelectElement(SaleOrderFormViewPageLocators.INVOICE_STATUS)
    partner_el = Many2One(
        SaleOrderFormViewPageLocators.PARTNER, dialog=PartnerDialogForm
    )
    order_line_el = One2Many(
        SaleOrderFormViewPageLocators.ORDER_LINE, row_view=SaleOrderLineRowView
    )

    def send_quotation(self, timeout=DEFAULT_TIMOUT_ACTION):
        self.click(SaleOrderFormViewPageLocators.QUOTATION_SEND, timeout=timeout)
        self.mail_compose_send_message()

    def confirm(self, timeout=DEFAULT_TIMOUT_ACTION):
        locator = SaleOrderFormViewPageLocators.PRIMARY_CONFIRM
        if self.state_el.value == "draft":
            locator = SaleOrderFormViewPageLocators.SECONDARY_CONFIRM
        self.click(locator, timeout=timeout)

    def create_invoice_wizard(self, timeout=DEFAULT_TIMOUT_ACTION):
        self.click(SaleOrderFormViewPageLocators.CREATE_INVOICE, timeout=timeout)
        return InvoiceOrderWizardForm(self.driver, timeout=timeout)


class SaleOrderListViewPageLocators:
    PAGE_SELECTOR = (By.CSS_SELECTOR, "div.o_list_view")


class SaleOrderListViewPage(BaseSalesPage, ListViewMixin):
    _page_selector = SaleOrderListViewPageLocators.PAGE_SELECTOR
    _form_view = SaleOrderFormViewPage


class ProductTemplateFormViewPageLocators:
    PAGE_SELECTOR = (By.CSS_SELECTOR, "div.o_form_view")

    NAME = (By.NAME, "name")
    UOM = (By.NAME, "uom_id")
    UOM_PO = (By.NAME, "uom_po_id")


class ProductTemplateFormViewPage(BaseSalesPage, FormViewMixin):
    _page_selector = ProductTemplateFormViewPageLocators.PAGE_SELECTOR

    name_el = InputElement(ProductTemplateFormViewPageLocators.NAME)
    uom_el = Many2One(ProductTemplateFormViewPageLocators.UOM)
    uom_po_el = Many2One(ProductTemplateFormViewPageLocators.UOM_PO)


class ProductTemplateKanbanViewPageLocators:
    PAGE_SELECTOR = (By.CSS_SELECTOR, "div.o_kanban_view")
    # PAGE_SELECTOR = (By.XPATH, "//nav/a[contains(text(), 'Articles')]")


class ProductTemplateKanbanViewPage(BaseSalesPage, KanbanViewMixin):
    _page_selector = ProductTemplateKanbanViewPageLocators.PAGE_SELECTOR
    _form_view = ProductTemplateFormViewPage


class ProductTemplateListViewPageLocators:
    PAGE_SELECTOR = (By.CSS_SELECTOR, "div.o_list_view")


class ProductTemplateListViewPage(BaseSalesPage, ListViewMixin):
    _page_selector = ProductTemplateListViewPageLocators.PAGE_SELECTOR
    _form_view = ProductTemplateFormViewPage
