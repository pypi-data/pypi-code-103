from pywyse.client import Client 
from pywyse.exceptions import PywyseException


class Opportunity(Client):
    
    def __init__(self):
        super(Opportunity, self).__init__()

    def get_opportunities(self, **kwargs): 
        return self.cw_get('/sales/opportunities', **kwargs).json()

    def get_opportunity(self, id, **kwargs): 
        kwargs['conditions'] = 'id = %s' % id
        kwargs['pageSize'] = '1'
        return self.get_opportunities(**kwargs)