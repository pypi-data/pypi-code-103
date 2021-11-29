import json

from .common_service import BaseOnaroRestCaseAdmin


class CRMLeadServiceRestCase(BaseOnaroRestCaseAdmin):

    def test_route_right_create(self):
        url = "/api/crm-lead"
        data = {
            "partner_name": "Aida Sanahuja",
            "dni": "62151786J",
            "birth_date": "25/8/1996",
            "phone": "641708221",
            "email_from": "1k3b85mo0@hotmail.com",
            "street": "Carrer del Rec",
            "invoice_address": "Carrer del Bruc",
            "portability_number": "687608770",
            "iban": "ES6621000418401234567891",
            "language": "es",
            "policy_accepted": True,
            "tag_ids": [1,2],
            "description": "Crm lead line notes",
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        crm_lead = self.env["crm.lead"].browse(content["id"])
        self.assertEquals(crm_lead.partner_name, data["partner_name"])
        self.assertEquals(crm_lead.dni, data["dni"])
        self.assertEquals(crm_lead.birth_date, data["birth_date"])
        self.assertEquals(crm_lead.phone, data["phone"])
        self.assertEquals(crm_lead.email_from, data["email_from"])
        self.assertEquals(crm_lead.street, data["street"])
        self.assertEquals(crm_lead.zip, '20560')
        self.assertEquals(crm_lead.city, 'Oñati')
        self.assertEquals(crm_lead.state_id, self.ref("base.state_es_ss").id)
        self.assertEquals(crm_lead.invoice_address, data["invoice_address"])
        self.assertEquals(crm_lead.portability_number, data["portability_number"])
        self.assertEquals(crm_lead.iban, data["iban"])
        self.assertEquals(crm_lead.language, data["language"])
        self.assertEquals(crm_lead.policy_accepted, data["policy_accepted"])
        self.assertEquals(crm_lead.tag_ids.ids, data["tag_ids"])
        self.assertEquals(crm_lead.description, data["description"])
