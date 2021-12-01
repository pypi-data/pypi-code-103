import requests
import os 
from pywyse import __conf

sell_conf = __conf

class Sell: 
    def __init__(self, conf=sell_conf): 
        self.conf=conf

    def base_url(self, endpoint=''): 
        url = f"https://sellapi.quosalsell.com"
        url = url + endpoint 
        return url 
    
    def headers(self, **kwargs): 
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.conf['sell_auth'],
            **kwargs 
        }
        return headers 
    
    def get_sell(self, endpoint='', verbose=True, **kwargs):
        headers = kwargs.pop('headers', {})
        headers = self.headers(**headers) 
        if verbose:
            print(endpoint)
            print(headers)
            print(kwargs)
        return requests.get(self.base_url(endpoint), headers=headers, params=kwargs)

    def translate(self, id): 
        """Translate CW Opportunity id to sell id."""
        condition = 'crmOpportunityID = %s' % str(id) 
        includeFields = 'name,quoteNumber,quoteVersion,id,approvalStatus'
        return self.get_quotes(conditions=condition, pageSize=1, includeFields=includeFields)

    def get_quotes(self, **kwargs):
        return self.get_sell('/api/quotes', **kwargs).json()
        

    def get_quote(self, id, **kwargs): 
        endpoint = '/api/quotes/' + str(id)
        return self.get_sell(endpoint, **kwargs).json()
