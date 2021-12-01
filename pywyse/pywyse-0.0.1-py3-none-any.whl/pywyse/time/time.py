from pywyse.client import Client 


class Time(Client): 

    def __init__(self): 
        super(Time, self).__init__()

    def get_timesheets(self, endpoint='/time/sheets', **kwargs):
        self.cw_get(endpoint, **kwargs)

    def get_timeentries(self, endpoint='/time/entries', **kwargs):
        self.cw_get(endpoint, **kwargs) 