from pywyse import project
from pywyse.service import Ticket
from pywyse.service.models import PurchaseTicket
import pytest 

def test_post(): 
    tickets = Ticket().get_tickets(pageSize=1000, page=20)
    assert isinstance(tickets, list)
    assert len(tickets) == 1000

    ticket = Ticket().get_ticket(tickets[999]['id'])
    assert isinstance(ticket, dict)

    # Defaults to C9Smart company
    simple_ticket = PurchaseTicket(summary="HelloWorld!").to_dict()

    # Project ticket with no notes 
    project_ticket = PurchaseTicket(
        summary='ProjectInfo',
        company={'id':'2'}, 
        project_id='5866'
        ).to_dict()

    # Project ticket with notes 
    project_ticket_notes = PurchaseTicket(
        summary='ProjectInfo',
        company={'id':'2'}, 
        project_id='5866',
        notes='Project ticket with notes'
        ).to_dict()

    
    # resp = Ticket().create_ticket(Ticket=simple_ticket)
    # resp1 = Ticket().create_ticket(Ticket=project_ticket)
    # resp2 = Ticket().create_ticket(Ticket=project_ticket_notes)
    
    # ticket_notes = Ticket().get_ticket_association(resp2)
    # assert isinstance(ticket_notes, list) 

