from pywyse.client import Client 

class CallBack(Client): 

    def __init__(self): 
        super(CallBack, self).__init__()
        self.endpoint = '/system/callbacks/' 

    def get_callbacks(self, endpoint='', **kwargs): 
        if not endpoint: 
            endpoint = self.endpoint 
        return self.cw_get(endpoint, **kwargs).json() 

    def get_callback(self, callback, **kwargs): 
        endpoint = self.endpoint + str(callback)
        return self.get_callbacks(endpoint, **kwargs)


    def create(self, callback, **kwargs): 
        """
        From docs: 
            Id: The database record id of the callback, this is automatically assigned.
            Description: This is used to label the callback's usage.
            URL: This is the URL ConnectWise Manage will send the GET payload to.
            ObjectId: The ObjectId should be the Id of whatever record you are subscribing to. 
                This should be set to 1 when using a level of Owner. 
            Type: This is the specific type of record such as Company, Ticket, Contact, 
                etc... See the associated table for all values.
            Level: The level is used to determine how granular the callback subscription will be.
            MemberId: This is a read only value that shows who initially created the Callback.
            InactiveFlag: Used to determine if the callback is active and sending requests.

            Success: status_code == 204
        """
        return self.cw_post(self.endpoint, body=callback, **kwargs)

    def void(self, callback_id, **kwargs):
        endpoint = self.endpoint + str(callback_id)
        return self.cw_delete(endpoint, **kwargs)
    
class Board(Client): 

    def __init__(self): 
        super(Board, self).__init__()
        self.endpoint = '/service/boards/' 

    def get_boards(self, fields='', **kwargs): 
        if not fields: 
            fields='id,name'
        return self.cw_get(self.endpoint, fields=fields, **kwargs).json()

class Member(Client):

    def __init__(self): 
        super(Member, self).__init__()
        self.endpoint = '/system/members'

    def get_members(self, fields='', **kwargs): 
        if not fields:
            fields='id,identifier,firstName,lastName,employeeIdentifer,inactiveFlag'
        return self.cw_get(self.endpoint, fields=fields, **kwargs).json()

