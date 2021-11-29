from odoo import api, fields, models
from datetime import date


class ContractContract(models.Model):
    _inherit = "contract.contract"

    product_category_id = fields.Many2one(
        "product.category",
        string="Product Category",
    )
    broadband_isp_info = fields.Many2one(
        "broadband.isp.info",
        string="Broadband ISP Info"
    )
    mobile_isp_info = fields.Many2one(
        "mobile.isp.info",
        string="Mobile ISP Info"
    )
    is_mobile = fields.Boolean(
        compute='_get_is_mobile',
        store=True
    )
    is_broadband = fields.Boolean(
        compute='_get_is_broadband',
        store=True
    )
    is_landline = fields.Boolean(
        compute='_get_is_landline',
        store=True
    )
    current_tariff = fields.Many2one(
        'product.product',
        compute='_compute_current_contract_line_tariff',
        store=True
    )

    @api.depends('product_category_id')
    def _get_is_mobile(self):
        mobile = self.env.ref('telecom.mobile_service')
        for record in self:
            record.is_mobile = (
                mobile.id == record.product_category_id.id
            )

    @api.depends('product_category_id')
    def _get_is_broadband(self):
        adsl = self.env.ref('telecom.broadband_adsl_service')
        fiber = self.env.ref('telecom.broadband_fiber_service')
        radiofrequency = self.env.ref('telecom.broadband_radiofrequency_service')
        for record in self:
            record.is_broadband = (
                record.product_category_id.id in [adsl.id, fiber.id, radiofrequency.id]
            )

    @api.depends('product_category_id')
    def _get_is_landline(self):
        landline = self.env.ref('telecom.landline_service')
        for record in self:
            record.is_landline = (
                landline.id == record.product_category_id.id
            )

    @api.depends('product_category_id')
    def _compute_current_contract_line_tariff(self):
        service_categs = [
            self.env.ref('telecom.mobile_service').id,
            self.env.ref('telecom.landline_service').id,
            self.env.ref('telecom.broadband_adsl_service').id,
            self.env.ref('telecom.broadband_fiber_service').id,
            self.env.ref('telecom.broadband_radiofrequency_service').id
        ]
        for record in self:
            line = self.env["contract.line"].search([
                ("contract_id", "=", record.id),
                ("product_id.categ_id", "in", service_categs),
                ("date_start",'<=', date.today().strftime('%Y-%m-%d')),
                '|',
                ('date_end', '>', date.today().strftime('%Y-%m-%d')),
                ('date_end', '=', False)
            ], limit=1)

            if line:
                record.current_tariff = line.product_id.id
