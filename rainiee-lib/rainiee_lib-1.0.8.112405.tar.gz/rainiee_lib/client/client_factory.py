import traceback

from rainiee_data.data_client import DataClient
from rainiee_rest_client.rest_client import RestClient

from ..lib import utils

client_init_dict = {
    'rainiee_data_client':'DataClient(self.username, self.password)',
    'rainiee_compute_client':'RestClient(self.username, self.password).choice_rainiee_compute().login()'
}
client_dict = {}

class ClientFactory(object):
    def __init__(self):
        self.username = 'hhh7788518'
        self.password = 'hu7788518'

    def rainiee_data_client(self):
        return self.__get_client(self.rainiee_data_client.__name__)

    def rainiee_compute_client(self):
        return self.__get_client(self.rainiee_compute_client.__name__)

    def init_all_client(self):
        for key,value in client_init_dict.items():
            self.__init_client(key,value)


    def __get_client(self,key):
        client = client_dict.get(key)
        if client is None:
            self.__init_client(key,client_init_dict[key])
            client = client_dict.get(key)
        return client

    def __init_client(self,key,value):
        try:
            client_dict[key] = eval(value)
        except Exception as e:
            utils.error(traceback.format_exc())

