import pytest 
from pywyse.utils import filter_ticket
from pywyse.exceptions import PywyseException

x = [
    {'id': 17347, 'description': 'Delivery', 'internalNotes': '398828', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    {'id': 17347, 'description': 'Delivery', 'internalNotes': 'This isome kjelr398828', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    {'id': 17347, 'description': 'Delivery', 'internalNotes': '398828Thisaslkjasd', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    {'id': 17347, 'description': 'Delivery', 'internalNotes': 'PartNo321\n398828 More text\n\n', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    {'id': 17347, 'description': 'Delivery', 'internalNotes': '3123121g2\b\bPartNo321\n398828 More text\n\n', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    {'id': 17347, 'description': 'Delivery', 'internalNotes': '', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},
    ]

y = [{'id': 17347, 'description': 'Delivery', 'internalNotes': '', 'product': 'LSD - 001', 'quantity': 1.0, 'po_id': 7264},]

p = [
    {'id': 16813, 'description': 'Cisco Meraki MX84 Cloud Managed - Firewall', 'internalNotes': '394963', 'product': 'MX84-HW', 'quantity': 1.0, 'po_id': 7026}, 
    {'id': 16815, 'description': 'Cisco Meraki MS120-48LP Cloud Managed - 48P Network Switch', 'internalNotes': '394963', 'product': 'MS120-48LP-HW', 'quantity': 1.0, 'po_id': 7026},
    {'id': 16816, 'description': 'Meraki Enterprise MS120-48LP - ', 'internalNotes': '394963', 'product': 'LIC-MS120-48LP-1YR', 'quantity': 1.0, 'po_id': 7026},
    {'id': 16817, 'description': 'Cisco Meraki MS120-24LP Cloud Managed - 24P Network Switch', 'internalNotes': '394963', 'product': 'MS120-24P-HW', 'quantity': 2.0, 'po_id': 7026},
    {'id': 16818, 'description': 'Meraki Enterprise MS120-24LP - Subscription License ( 1 Year )', 'internalNotes': '394963', 'product': 'LIC-MS120-24P-1YR', 'quantity': 2.0, 'po_id': 7026}, 
    {'id': 16819, 'description': 'Cisco Meraki MR42 Cloud Managed Wireless Access Point', 'internalNotes': '394963', 'product': 'MR42-HW', 'quantity': 7.0, 'po_id': 7026}, 
    {'id': 16821, 'description': 'Cisco Meraki Outdoor Acess Point - IP67 Rugged ', 'internalNotes': '394963', 'product': 'MR70-HW', 'quantity': 3.0, 'po_id': 7026}]

def test_filter(): 
    filter_ticket(x)
    filter_ticket(p)
    
    with pytest.raises(PywyseException):
        filter_ticket(y)

