from odoo import models, fields, api


class CRMLeadLineCreationWizard(models.TransientModel):
    _name = 'crm.lead.line.creation.wizard'
    available_product_category_ids = fields.Many2many(
        'product.category',
        string='Available Product Categories',
    )
    product_category_id = fields.Many2one('product.category', 'Product Category')
    product_id = fields.Many2one('product.product', 'Product')
    service_street = fields.Char(string='Service Street')
    lead_id = fields.Many2one('crm.lead')
    phone_number = fields.Char(string='Phone Number')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['lead_id'] = self.env.context['active_id']
        defaults['available_product_category_ids'] = self.env['product.template'].search([]).mapped('categ_id.id')
        return defaults

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        self.product_id = False
        self.service_street = False

    def button_creation(self):
        if self.product_category_id in [self.env.ref('telecom.mobile_service')]:
            mobile_isp_info_args = {
                "phone_number": self.phone_number
            }
            mobile_isp_info = self.env['mobile.isp.info'].create(mobile_isp_info_args)
            lead_line_args = {
                "name": self.product_id.name,
                'lead_id': self.lead_id.id,
                'mobile_isp_info': mobile_isp_info.id,
                'product_id': self.product_id.id,
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "category_id": self.product_id.categ_id.id
            }
            self.env['crm.lead.line'].create(lead_line_args)
        else:
            broadband_isp_info_args = {
                'service_street': self.service_street
            }
            broadband_isp_info = self.env['broadband.isp.info'].create(broadband_isp_info_args)
            lead_line_args = {
                "name": self.product_id.name,
                'lead_id': self.lead_id.id,
                'broadband_isp_info': broadband_isp_info.id,
                'product_id': self.product_id.id,
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "category_id": self.product_id.categ_id.id
            }
            self.env['crm.lead.line'].create(lead_line_args)

