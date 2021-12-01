from pywyse.client import Client 
from pywyse.exceptions import PywyseException
import os, tempfile


class Invoicing(Client): 
    def __init__(self):
        super(Invoicing, self).__init__()
    
    def get_invoices(self, endpoint='/finance/invoices', **kwargs): 
        return self.cw_get(endpoint, **kwargs).json()

    def get_invoice(self, invoice, **kwargs): 
        kwargs['conditions'] = f"invoiceNumber = '{invoice}'"
        kwargs['pageSize'] = '1'

        return self.get_invoices(**kwargs)
    
    def get_invoice_pdf(self, invoice, **kwargs):
        inv = self.get_invoice(invoice) 
        endpoint = '/finance/invoices/' + str(inv[0]['id']) + '/pdf'

        kwargs['headers'] = {'Accept': 'application/pdf'}
        resp = self.cw_get(endpoint, **kwargs)
        
        tmp = tempfile.mkstemp(suffix='.pdf', prefix=str(invoice))
        
        with open(tmp[1], 'wb') as s_inv:
            s_inv.write(resp.content)
    
        return {"invoice": invoice, "path": tmp[1]}