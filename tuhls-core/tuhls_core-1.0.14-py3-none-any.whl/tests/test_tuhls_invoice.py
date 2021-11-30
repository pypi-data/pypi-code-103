import uuid

from django.test import TestCase
from pdfminer.high_level import extract_text

from tuhls_invoice import models
from tuhls_invoice.services import invoice_to_pdf


class InvoiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = uuid.uuid4()

    @staticmethod
    def create_fake_invoice(user, invoice_type, num_products):
        invoice = models.Invoice.objects.create(
            user=user,
            type=invoice_type,
            city="some_city",
            zip_code="0815",
            state="some_state",
        )
        for x in range(num_products):
            models.InvoiceDetail.objects.create(
                invoice=invoice,
                name=f"product {x}",
                description=f"nice product {x}",
                amount=5,
            )
        return invoice

    def test_invoices(self):
        invoice = self.create_fake_invoice(self.user, models.Invoice.Types.INVOICE, 5)
        self.assertEqual(25, invoice.total())
        self.assertEqual("i-000001", invoice.get_invoice_number())
        self.assertEqual("invoice", invoice.get_type_name())

        models.InvoiceDetail.objects.create(
            invoice=invoice,
            name="credit",
            description="nice credit",
            amount=-15,
        )
        self.assertEqual(10, invoice.total())

        for i in [
            [self.user, models.Invoice.Types.ESTIMATE, 3, 15, "e-000001", "estimate"],
            [self.user, models.Invoice.Types.ESTIMATE, 7, 35, "e-000002", "estimate"],
            [self.user, models.Invoice.Types.INVOICE, 1, 5, "i-000002", "invoice"],
            [self.user, models.Invoice.Types.ESTIMATE, 2, 10, "e-000003", "estimate"],
        ]:
            invoice = self.create_fake_invoice(i[0], i[1], i[2])
            self.assertEqual(i[3], invoice.total())
            self.assertEqual(i[4], invoice.get_invoice_number())
            self.assertEqual(i[5], invoice.get_type_name())

    def test_pdf(self):
        invoice = self.create_fake_invoice(self.user, models.Invoice.Types.INVOICE, 5)
        txt = extract_text(invoice_to_pdf(invoice))
        self.assertIn("Total", txt)
        self.assertIn("$ 25.00", txt)
        self.assertIn("INVOICE", txt)
