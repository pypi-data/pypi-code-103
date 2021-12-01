from datetime import datetime 
from typing import ValuesView
from pywyse.client import Client 

class Procurement(Client):
    
    def __init__(self, *args, **kwargs): 
        super(Procurement, self).__init__(*args, **kwargs) 
        self.endpoint = '/finance/accounting'
        self.batch_ids = [] 


    def count_unposted(self, **kwargs): 
        """
        Count the number of items in the Procurement Interface to be transferred. 
        """
        endpoint = self.build_url(self.endpoint, 'unpostedprocurement/count/')
        try: 
            resp = self.cw_get(endpoint, **kwargs).json()
        except Exception as e: 
            raise ValueError("Could not connect")

        return resp

    def get_unposted(self, **kwargs): 
        """
        Get the procurement summary to be transferred. 
        """
        endpoint = self.build_url(self.endpoint, 'unpostedprocurement/')
        try: 
            resp = self.cw_get(endpoint, **kwargs).json()
        except Exception as e: 
            raise ValueError('Could not connect')
        
        return resp 

    def get_batch_ids(self, ids=None):
        """
        Batching the current accounting interface
        """ 
        if ids is None:
            resp_interface = Procurement().get_unposted(fields='unpostedProductId', pageSize=1000)
            ids = [c['unpostedProductId'] for c in resp_interface]
        try: 
            self.batch_ids = [c for c in ids]
        except Exception as e: 
            print(e) 
            raise ValueError('Missing ids')


    def soft_batch(self, **kwargs): 
        if not self.batch_ids: 
            self.get_batch_ids()
        
        soft_batch = {
            'batchIdentifier': 'POS' + datetime.now().strftime('%Y%m%d'),
            'exportProductsFlag': True,
            'includedProductIds': self.batch_ids
        }

        endpoint = self.build_url(self.endpoint, 'export/')
        return self.cw_post(endpoint, body=soft_batch).json()
    

    def batch(self, ids, **kwargs): 

        ids = [c for c in ids]
        batch = {
            # What the batch will be named
            'batchIdentifier':'P' + datetime.now().strftime('%y%m%d%H%M%S'),
            'glInterfaceIdentifier':'P' + datetime.now().strftime('%y%m%d%H%M%S'),
            'exportInvoicesFlag':False,
            'exportExpensesFlag':False,
            'exportProductsFlag':True,
            'processedRecordIds':ids,
            'summarizeExpenses':False,
        }
        endpoint = self.build_url(self.endpoint, 'batches')
        self.cw_post(endpoint, body = batch, **kwargs)
