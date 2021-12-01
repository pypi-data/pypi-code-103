import os 
import re 

from pywyse.exceptions import PywyseException

def filter_ticket(resp: list) -> list:
    """
    Take a list of line items and return unique internal notes as a list.
    [{'id': 17347, 'description': 'Delivery', 'internalNotes': '398828', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264}]
    """ 
    
    r = [i.get('internalNotes', 'empty') for i in resp]
    resp = list(set([item for sublist in [re.findall(r'^(\d{6})', c) for c in r] for item in sublist]))
    
    if len(resp) == 0:
        raise PywyseException("No response")
        
    return resp 
