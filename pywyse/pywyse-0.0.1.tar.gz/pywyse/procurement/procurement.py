from .models import ProcurementModel

from pywyse.client import Client
from pywyse.service import Ticket
from pywyse.exceptions import PywyseException

class Procurement(Client): 

    def __init__(self): 
        super(Procurement, self).__init__()


    def get_purchaseorders(self, endpoint = '/procurement/purchaseorders', **kwargs) -> list:
        """
        Returns a list of dictionaries.
        """
        return self.cw_get(endpoint=endpoint, **kwargs).json()

    def get_purchaseorder(self, purchase_order=None, **kwargs) -> dict:
        """
        Should only return a single purchase order. No match will raise an exception.
        """

        kwargs['conditions'] = "poNumber='C9PO%s'" % purchase_order
        kwargs['pageSize'] = 1
        kwargs['fields'] = 'id,vendorCompany/name'

        resp = self.get_purchaseorders(**kwargs)

        try: 
            return resp[0]
        except IndexError:
            raise PywyseException("Invalid purchase order")
        

    def get_purchaseorder_lines(self, purchase_order, **kwargs) -> list: 
        po_id = self.get_purchaseorder(purchase_order)
        endpoint = f"/procurement/purchaseorders/{po_id['id']}/lineitems"
        kwargs['fields'] = "id,quantity,product/identifier,description,internalNotes,receivedStatus"
 
        resp = self.cw_get(endpoint=endpoint, **kwargs).json()
      
        for i in range(len(resp)):
            resp[i]['product'] = resp[i]["product"]["identifier"]
            resp[i]['po_id'] = po_id['id']
            resp[i]['vendorName'] = po_id['vendorCompany']['name']

        return resp
    
    def get_purchaseorder_line(self, po_id, line_id, **kwargs): 
        
        endpoint = f"/procurement/purchaseorders/{po_id}/lineitems/{line_id}"
        kwargs['fields'] = "id,quantity"
        kwargs['pageSize'] = "1"
 
        resp = self.cw_get(endpoint=endpoint, **kwargs).json()
      
        return resp


    def get_product_meta(self, ticket, **kwargs):
        """
        Product response: 
            [{'project': {'id': 5981, 'name': 'AV'}, 'company': {'name': 'Rosenberg, Robert Residence'}}]
        Subcontractor:
            [{'company': {'name': 'Hilldun Corp'}, 'summary': 'SUB:  36 East 31st Cabling:  PO Request: Lightspeed'}]
        """

        purch_tick = Ticket().get_ticket(ticket)

        kwargs['conditions'] = f"company/id = {purch_tick['company']} and internalNotes contains '{ticket}'"
        kwargs['fields'] = 'project/name,project/id,company/name'
        kwargs['pageSize'] = '1'
       
        endpoint = '/procurement/products'
        resp = self.cw_get(endpoint, **kwargs).json()

        resp[0]['summary'] = purch_tick.get('summary', '')

        return resp 


    def receive_product(self, purchase_id, line_id, receive_quantity, **kwargs): 
        """
        Add a decorator to send to slack. 
        Patch: /procurement/purchaseorders/{parentId}/lineitems/{id}
        {'id': '17443', 'internalNotes': None, 'product': 'QS-WLB', 'quantity': 5, 'quantityReceived': 0}

      
        When receiving partial quantity on a fully received item, a new item with quantity: 0 will be created.
        """
        # Test if it's fully or partially received
        line_qty = self.get_purchaseorder_line(purchase_id, line_id)

        if line_qty['quantity'] == receive_quantity:
            status =  'FullyReceived'
        else: 
            status = 'PartiallyReceiveCloneRest'

        kwargs['body'] = [
            {
                'op': 'replace',
                'path': 'receivedQuantity',
                'value': str(receive_quantity)
                }, 
            {
                'op': 'replace',
                'path': 'receivedStatus',
                'value': status
                } 
            ]

        endpoint = f'/procurement/purchaseorders/{str(purchase_id)}/lineitems/{str(line_id)}'

        try: 
            resp = self.cw_patch(endpoint, **kwargs)
            
        except Exception as e: 
            print("Error closing poid: %s" % purchase_id)
            print(e)
            resp = False

        return resp 

    def purchase_order(self, endpoint='/procurement/purchaseorders', **kwargs): 
        resp = self.cw_post(endpoint, **kwargs)
        return resp

# class PurchaseOrder(PO, Client): 
#     def __init__(self, model=''): 
