import pytest 
from pywyse.invoicing import Invoicing 
from pathlib import Path

def test_invoices(): 
    invoices = Invoicing().get_invoices(pageSize=1000, page=2)

    assert isinstance(invoices, list)
    assert len(invoices) == 1000

    invoice = Invoicing().get_invoice(invoices[0].get('invoiceNumber'))
    assert len(invoice) == 1
    assert isinstance(invoice, list)

    resp = Invoicing().get_invoice_pdf(invoice[0].get('invoiceNumber'))
    assert Path.exists(Path(resp['path']))
    
    