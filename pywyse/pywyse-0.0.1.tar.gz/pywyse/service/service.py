from pywyse.client import Client 
from .models import PurchaseTicket

class Ticket(Client): 

    def __init__(self):
        super(Ticket, self).__init__()
        self.endpoint = '/service/tickets/' 

    def get_tickets(self, endpoint='', **kwargs): 
        if not endpoint:
            endpoint = self.endpoint
        return self.cw_get(endpoint, **kwargs).json()

    def get_ticket(self, ticket, fields='id,summary,company/id,company/name', **kwargs): 
        endpoint = self.endpoint + str(ticket)
        resp = self.get_tickets(endpoint, fields=fields, **kwargs)
        try:
            resp['companyName']= resp['company']['name']
            resp['company']= resp['company']['id']
        except Exception as e: 
            print(e)
            
        return resp

    def get_ticket_association(self, ticket, **kwargs): 
        """Returns the tickets project. Why can't purchase tickets be converted to project
        tickets.
        """
        endpoint = self.endpoint + str(ticket) + '/notes/'
        c = 'member/id=%s' % self.conf.get('cw_integration', '')
        fields = 'text,id'
        print(endpoint)
        resp = self.cw_get(endpoint, conditions=c, fields=fields,**kwargs)
        return resp.json() 

    def create_ticket(self, Ticket, **kwargs): 
        endpoint = self.endpoint

        notes = Ticket.pop('notes', '')
        project_id = Ticket.pop('project_description', '')
        resp = self.cw_post(endpoint, body=Ticket, **kwargs)
        
        if resp.status_code == 201 and project_id: 
            ticket_id = endpoint + '/' + str(resp.json()['id']) + '/notes/'
            print(ticket_id)
            body = {'text': project_id, 'internalAnalysisFlag': True}
            resp = self.cw_post(ticket_id, body=body).json()
            print(resp)
            if notes:
                body = {'text': notes, 'detailDescriptionFlag': True}
                r = self.cw_post(ticket_id, body=body) 
                return r.json()['ticketId']

            else: 
                return resp['ticketId']
        else: 
            try: 
                return resp.json()['id']
            except Exception as e: 
                print(e) 
                return resp
