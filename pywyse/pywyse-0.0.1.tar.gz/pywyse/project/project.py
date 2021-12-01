from pywyse.exceptions import PywyseException
from pywyse.client import Client

class Project(Client): 

    def __init__(self): 
        super(Project, self).__init__()
        self.endpoint = '/project/projects/' 

    def get_projects(self, endpoint='',  **kwargs): 
        if not endpoint: 
            endpoint = self.endpoint
        return self.cw_get(endpoint, **kwargs).json()

    def get_project(self, id, **kwargs):
        endpoint = self.endpoint + str(id)
        return self.get_projects(endpoint, **kwargs)

    def get_open_projects(self, conditions='closedFlag=false', pageSize = 1000, **kwargs): 
        return self.get_projects(pageSize=pageSize, conditions=conditions, **kwargs)
    
    def get_products(self, project_id, **kwargs):
        project_id = 'project/id=%s' % str(project_id)
        if kwargs.get('conditions'): 
            kwargs['conditions'] = project_id + ' and ' + kwargs['conditions']         
        else: 
            kwargs['conditions'] = project_id
            
        endpoint = '/procurement/products/'

        resp = self.cw_get(endpoint, **kwargs).json()
        try: 
            for i in range(len(resp)):
                resp[i]['picked'] = self.get_product_pickedstatus(resp[i]['id'])
            return resp 
        except Exception: 
            return resp 
        


    def get_product_pickedstatus(self, product_id, **kwargs): 
        endpoint = '/procurement/products/' + str(product_id) + '/pickingShippingDetails/'
        resp = self.cw_get(endpoint, fields='pickedQuantity').json()
        try: 
            return resp[0].get('pickedQuantity', '0')
        except: 
            return resp 
