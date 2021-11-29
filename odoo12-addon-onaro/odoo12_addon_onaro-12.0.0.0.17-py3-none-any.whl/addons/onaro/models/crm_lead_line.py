from odoo import models


class CRMLeadLine(models.Model):
    _inherit = 'crm.lead.line'

    # Create an invoice address for the partner created
    def _post_partner_creation_hook(self, partner):
        if self.lead_id.invoice_address:
            self._create_invoice_address(partner)

    # Create an invoice address for the partner updated,
    # if it doesn't exist already
    def _post_partner_update_hook(self, partner):
        if self.lead_id.invoice_address:
            invoice_child_ids =  self.env["res.partner"].search([
                ('parent_id', '=', partner.id),
                ('type', '=', 'invoice'),
            ])
            if not invoice_child_ids:
                self._create_invoice_address(partner)

    def _create_invoice_address(self, partner):
        self.env["res.partner"].create({
            "type": 'invoice',
            "parent_id": partner.id,
            "street": self.lead_id.invoice_address,
            "zip": self.lead_id.zip,
            "city": self.lead_id.city,
            "state_id": self.lead_id.state_id.id,
        })
