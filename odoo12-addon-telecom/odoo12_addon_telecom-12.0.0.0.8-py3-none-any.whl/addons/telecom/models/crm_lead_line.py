from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number


class CRMLeadLine(models.Model):
    _inherit = 'crm.lead.line'

    broadband_isp_info = fields.Many2one(
        'broadband.isp.info',
        string='Broadband ISP Info'
    )
    mobile_isp_info = fields.Many2one(
        'mobile.isp.info',
        string='Mobile ISP Info'
    )

    is_mobile = fields.Boolean(
        compute='_get_is_mobile',
        store=True
    )
    is_adsl = fields.Boolean(
        compute='_get_is_adsl',
    )
    is_fiber = fields.Boolean(
        compute='_get_is_fiber',
    )
    supplier_external_reference = fields.Char(
        compute='_get_supplier_external_reference',
    )

    def start_provisioning(self):
        # Create or update Partner
        partner = self._create_or_update_partner()
        # Create SaleOrder
        order = self._create_order(partner)

    def _create_or_update_partner(self):
        """
        Create a partner with CRMLead info or update it if exists.
        """
        if self.lead_id.partner_id:
            return self._update_partner()
        # TODO: add error message
        if not self.lead_id.vat:
            raise ValidationError()

        partner = self.env["res.partner"].search([
            ("vat", "=", self.lead_id.vat)
        ], limit=1)

        if not partner:
            partner = self.env["res.partner"].create({
                "name": self.lead_id.name,
                "vat": self.lead_id.vat,
                "type": None,
                "email": self.lead_id.email_from,
                "phone": self.lead_id.phone,
                "street": self.lead_id.street,
                "zip": self.lead_id.zip,
                "city": self.lead_id.city,
                "state_id": self.lead_id.state_id.id,
                "lang": self.lead_id.language,
                "bank_ids": [(0, 0,
                    {
                        "acc_number": self.lead_id.iban
                    })
                ]
            })
            self._post_partner_creation_hook(partner)
            print("Partner created")

        # Assign partner to CRMLead
        self.lead_id.write({"partner_id": partner.id})
        print("Partner assigned to the CRMLead")

        return partner

    # Overwrite to add behavior after partner creation
    def _post_partner_creation_hook(self, partner):
        pass

    # Overwrite to add behavior after partner update
    def _post_partner_update_hook(self, partner):
        pass

    def _update_partner(self):
        partner = self.lead_id.partner_id
        partner_vars = {}

        partner_vars.update(self._partner_name())
        partner_vars.update(self._partner_vat())
        partner_vars.update(self._partner_email())
        partner_vars.update(self._partner_phone())
        partner_vars.update(self._partner_street())
        partner_vars.update(self._partner_zip())
        partner_vars.update(self._partner_city())
        partner_vars.update(self._partner_state_id())
        partner_vars.update(self._partner_lang())
        partner_vars.update(self._partner_acc_number())

        partner.write(partner_vars)
        self._post_partner_update_hook(partner)
        print("Partner updated")
        return partner

    def _partner_name(self):
        if self.lead_id.name and not self.lead_id.partner_id.name:
            return {"name": self.lead_id.name}
        else:
            return {}

    def _partner_vat(self):
        if self.lead_id.vat and not self.lead_id.partner_id.vat:
            return {"vat": self.lead_id.vat}
        else:
            return {}

    def _partner_email(self):
        if self.lead_id.email_from and not self.lead_id.partner_id.email:
            return {"email": self.lead_id.email_from}
        else:
            return {}

    def _partner_phone(self):
        if self.lead_id.phone and not self.lead_id.partner_id.phone:
            return {"phone": self.lead_id.phone}
        else:
            return {}

    def _partner_street(self):
        if self.lead_id.street and not self.lead_id.partner_id.street:
            return {"street": self.lead_id.street}
        else:
            return {}

    def _partner_zip(self):
        if self.lead_id.zip and not self.lead_id.partner_id.zip:
            return {"zip": self.lead_id.zip}
        else:
            return {}

    def _partner_city(self):
        if self.lead_id.city and not self.lead_id.partner_id.city:
            return {"city": self.lead_id.city}
        else:
            return {}

    def _partner_state_id(self):
        if self.lead_id.state_id.id and not self.lead_id.partner_id.state_id:
            return {"state_id": self.lead_id.state_id.id}
        else:
            return {}

    def _partner_lang(self):
        if self.lead_id.language and not self.lead_id.partner_id.lang:
            return {"lang": self.lead_id.language}
        else:
            return {}

    def _partner_acc_number(self):
        if self.lead_id.iban:
            same_acc_numbers = self.env["res.partner.bank"].search([
                ('partner_id', '=', self.lead_id.partner_id.id),
                ('sanitized_acc_number', '=', sanitize_account_number(self.lead_id.iban))
            ])
            if not same_acc_numbers:
                return {
                    "bank_ids": [(0, 0, {"acc_number": self.lead_id.iban})]
                }
            else:
                return {}

    def _create_order(self, partner):
        """
        Create a SaleOrder with CRMLead info.
        Create also the SaleOrderLines with the product and the services info.
        """
        # TODO: Check if order already exists
        #       Maybe we can store crm_lead_line_id in sale_order_line
        # order = self.env["sale.order"].search([
        #     ("partner_id", "=", partner.id),
        #     ("opportunity_id", "=", self.lead_id)
        # ], limit=1)

        product_id = self.product_id.id
        order_line_vals = {
            # TODO: Complete all SaleOrderLine data from the CRMLead and CRMLeadLine
            "product_id": product_id
        }
        self.env["sale.order"].create({
            # TODO: Complete all SaleOrder data from the CRMLead and CRMLeadLine
            "name": "{} - {}".format(partner.name, self.product_id.showed_name),
            "partner_id": partner.id,
            "opportunity_id": self.lead_id.id,
            "mobile_isp_info": self.mobile_isp_info.id,
            "broadband_isp_info": self.broadband_isp_info.id,
            "order_line": [(0, 0, order_line_vals)],
            "state": self.get_state(),
            "substate_id": self.get_substate_id(),
        })
        print("Opportunity created.")

    @api.depends('product_id')
    def _get_is_mobile(self):
        mobile = self.env.ref('telecom.mobile_service')
        for record in self:
            record.is_mobile = (
                mobile.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_adsl(self):
        adsl = self.env.ref('telecom.broadband_adsl_service')
        for record in self:
            record.is_adsl = (
                adsl.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_fiber(self):
        fiber = self.env.ref('telecom.broadband_fiber_service')
        for record in self:
            record.is_fiber = (
                fiber.id == record.product_id.product_tmpl_id.categ_id.id
            )

    # TODO: Maybe would be nice to move this to a Telecom config
    def get_state(self):
        return "draft"

    def get_substate_id(self):
        substate_target = self.get_substate_target()
        return self.env['base.substate'].search([
            ('target_state_value_id', '=', substate_target.id)
        ], order='sequence', limit=1).id

    def get_substate_target(self):
        substate_type = self.get_substate_type()
        return self.env['target.state.value'].search([
            ('base_substate_type_id', '=', substate_type.id),
            ('target_state_value', '=', self.get_state())
        ], limit=1)

    def get_substate_type(self):
        return self.env['base.substate.type'].search([
            ('model', '=', "sale.order"),
            ('product_category_ids', '=', self.product_id.product_tmpl_id.categ_id.id)
        ])

    def _get_supplier_external_reference(self):
        for record in self:
            if record.is_mobile:
                record.supplier_external_reference = record.mobile_isp_info.phone_number
            else:
                record.supplier_external_reference = record.broadband_isp_info.external_reference
