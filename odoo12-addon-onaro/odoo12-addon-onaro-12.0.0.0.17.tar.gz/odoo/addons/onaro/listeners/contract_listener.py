from odoo.addons.component.core import Component
from pycastiphone_client.resources.login import Login
from pycastiphone_client.resources.cliente import Cliente


class Contract(Component):
    _name = 'contract.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['contract.contract']

    def on_record_create(self, record, fields=None):
        if not record.partner_id.ref:
            cliente_data = ClientePresenter(record.partner_id).to_dict()
            login = Login.authenticate()
            castiphone_cliente = Cliente.create(login.token, **cliente_data)
            record.partner_id.write({
                'ref': castiphone_cliente.codigo
            })


class ClientePresenter():
    def __init__(self, partner):
        self.partner = partner

    def to_dict(self):
        data = {
            "razonSocial": self.partner.name,
            "cif": self.partner.vat,
            "correo": self.partner.email,
            "idioma": self.language(),
            "formaPago": 3,
            "tipoFactura": 4,
        }
        data.update(self.address())
        return data

    def language(self):
        if self.partner.lang == 'es_ES':
            language = 0
        else:
            language = 6
        return language

    def address(self):
        invoice_address = self.partner.search(
            [
                ("type", "=", "invoice"),
                ("parent_id", "=", self.partner.id),
            ],
        )
        if invoice_address:
            partner = invoice_address[0]
        else:
            partner = self.partner

        return {
            "direccion": partner.street,
            "poblacion": partner.city,
            "provincia": partner.state_id.name,
            "cPostal": partner.zip,
        }
