from odoo import api, fields, models

class ExternalIdMixin(models.AbstractModel):
    _name = "external.id.mixin"
    _description = "External ID Mixin"

    # do not access directly, always use get_api_external_id method
    _api_external_id = fields.Integer(string="External ID", index=True, required=False)
    external_id_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="External ID Sequence",
        required=False,
    )

    @api.multi
    def set_external_sequence(self):
        self.ensure_one()
        code = "%s.external.id" % self._name
        Sequence = self.env["ir.sequence"]
        # check if code was created for that model
        sequence = Sequence.search([("code", "=", code)])
        if not sequence:
            sequence = Sequence.sudo().create(
                {"name": code, "code": code, "number_next": 1}
            )

        self.sudo().write({"external_id_sequence_id": sequence.id})
        return True

    @api.multi
    def get_api_external_id(self):
        self.ensure_one()
        if not self.external_id_sequence_id:
            self.set_external_sequence()
        if not self._api_external_id:
            self.sudo().write(
                {"_api_external_id": self.external_id_sequence_id._next()}
            )
        return self._api_external_id
