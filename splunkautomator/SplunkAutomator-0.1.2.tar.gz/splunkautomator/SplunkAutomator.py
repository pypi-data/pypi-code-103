import requests
import warnings
#import pandas as pd
import json
import xml.etree.ElementTree as ET
from requests.models import Response

warnings.filterwarnings("ignore")

def get_response_object(status_code:int):
    if status_code==409:
        response = Response()
        response.code = "conflict"
        response.error_type = "conflict"
        response.status_code = status_code
        response._content = b'{ "status_code" : "409" ,"text":"name already exists"}'
        return response



class SplunkAlertAutomator():
    """This class can be used to build scripts to automate certain splunk tasks related to alerts and schedules searches.

    The class needs to be initialized with the Splunk URL and a username and password.
    The splunk user needs to have admin rights



    Attributes:
        splunk_ui (str): the splunk URL.
        username (str): the splunk user username.
        password (str): the splunk user password.
        splunk_app (str): the splunk app (url name) under which alerts should be created.

    """

    def __init__(self, splunk_uri: str, username: str, password: str, splunk_app: str = None) -> None:

        self.splunk_uri = splunk_uri
        self.username = username
        self.password = password
        self.splunk_app = splunk_app

        return

    def __create_alert(self, alert_configs):

        params = (
            ('output_mode', 'json'),
        )
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/',
                                 data=alert_configs,
                                 verify=False,
                                 params=params,
                                 auth=(self.username, self.password))

        return response

    def __delete_alert(self, alert_name:str):

        response = requests.delete(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/{alert_name}',
                                   verify=False,
                                   auth=(self.username, self.password))
        return response

    def __get_alert(self, alert_name:str):
        params = (
            ('output_mode', 'json'),
        )
        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/{alert_name}',
                                   verify=False,
                                   params=params,
                                   auth=(self.username, self.password))
        return response

    def __alert_exists(self, alert_name:str):
    
         response=self.__get_alert(alert_name=alert_name)

         return response.status_code==200

    def get_alert(self,alert_name:str):

        response=self.__get_alert(alert_name)
        response_payload=json.loads(response.content)

        r_alert_name=response_payload['entry'][0]['name']

        r_alert_configs=response_payload['entry'][0]['content']
        r_alert_configs['name']=r_alert_name # add name to configs, otherwise you cannot use this as input for .create_alert()
        r_alert_configs.pop('embed.enabled')# this key needs to be removed. otherwise the create alert method will raise an error (API does not accept it)

        r_alert_acl=response_payload['entry'][0]['acl']

        
        


        return r_alert_name,r_alert_configs,r_alert_acl

    def update_alert(self, alert_name, alert_update_config):

        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/{alert_name}',
                                 verify=False,
                                 data=alert_update_config,
                                 auth=(self.username, self.password))
        return response

    def update_alert_list(self, alert_list, alert_update_config):
        response_list = []
        for alert_name in alert_list:
            response = self.update_alert(
                alert_name=alert_name, alert_update_config=alert_update_config)
            response_list.append(response)
            print(alert_name)
        return response_list

    def change_alert_status(self, alert_name, disabled="0"):

        data = {
            'disabled': disabled
        }

        response = self.update_alert(alert_name, alert_update_config=data)

        return response

    def create_alert(self, alert_configs, overwrite=False):

        #this if block checks if there is already an alert with the specified name. 
        # This is necessary because the API will still create an alert with 201 status code if the acl has been changed
        if self.__alert_exists(alert_configs["name"]):
            if overwrite:
                print(f"Alert already exists. Overwrite flag=true, Deleting {alert_configs['name']} ...")
                self.__delete_alert(alert_configs['name'])
                print(f"Creating {alert_configs['name']} ...")
                response = self.__create_alert(alert_configs)
                print(f'{response.status_code}, Created alert_name: {alert_configs["name"]}')
                return response
            else:
                response=self.__get_alert(alert_configs["name"])
                response.status_code=409
                print(f'{response.status_code}, Alert already exists: {alert_configs["name"]}')

                return response

        response = self.__create_alert(alert_configs)

        if response.status_code == 409:
            print(f'{response.status_code}, Alert already exists: {alert_configs["name"]}')
            if overwrite:
                print(f"Alert already exists. Overwrite flag=true, Deleting {alert_configs['name']} ...")
                self.__delete_alert(alert_configs['name'])
                print(f"Creating {alert_configs['name']} ...")
                response = self.__create_alert(alert_configs)
                print(f'{response.status_code}, Created alert_name: {alert_configs["name"]}')
                return response
            else:
                return response
        print(f'{response.status_code}, Created alert_name: {alert_configs["name"]}')

        return response

    def delete_alert(self, alert_name):

        response = self.__delete_alert(alert_name)

        return response

    def get_alert_list(self, title_regex=["**"]):

        splunk_search = f"""
        |rest/servicesNS/-/{self.splunk_app}/saved/searches splunk_server=local
        | table disabled title"""

        for pattern in title_regex:
            splunk_search = f"""{splunk_search}
            | search title ="{pattern}"
            """
        print(splunk_search)
        data = {
            'search': splunk_search, 'output_mode': 'json'
        }
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/search/search/jobs/export',
                                 data=data,
                                 verify=False,
                                 auth=(self.username, self.password))

        text=response.text
        text_array=text.split('\n')
        _list=[json.loads(text_e) for text_e in text_array if text_e is not '']
        _list=[e['result']['title'] for e in _list] 
        _list=list(dict.fromkeys(_list))#the fastest way to dedup a list https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists/7961425#7961425
        return _list

    def delete_alert_list(self, alert_list):

        response_list = []
        for alert_name in alert_list:
            response = self.delete_alert(alert_name)
            response_list.append(response)
        return response_list

    def change_alert_list_status(self, alert_list, disabled="0"):
        response_list = []
        for alert_name in alert_list:
            response = self.change_alert_status(alert_name, disabled=disabled)
            response_list.append(response)
        return response_list

    def get_alert_acl(self, alert_name):

        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/{alert_name}/acl',
                                 verify=False,

                                 auth=(self.username, self.password))

        return response

    def change_alert_acl(self, alert_name, alert_acl_dict):

        
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/saved/searches/{alert_name}/acl',
                                 verify=False,
                                 data=alert_acl_dict,
                                 auth=(self.username, self.password))
        print(f"{response.status_code}, while changing ACL of {alert_name}")                         
        return response

    def change_alert_list_acl(self, alert_list, alert_acl_dict):

        response_list = []
        for alert_name in alert_list:
            response = self.change_alert_acl(alert_name, alert_acl_dict)
            response.title = alert_name
            response_list.append(response)
        return response_list




class SplunkDashboardAutomator():
    '''This class can be used to build scripts to automate certain splunk tasks related to dashboards.

    The class needs to be initialized with the Splunk URL and a username and password.
    The splunk user needs to have admin rights



    Attributes:
        splunk_ui (str): the splunk URL.
        username (str): the splunk user username.
        password (str): the splunk user password.
        splunk_app (str): the splunk app (url name) under which alerts should be created.'''

    def __init__(self, splunk_uri: str, username: str, password: str, splunk_app: str = None) -> None:
        self.splunk_uri = splunk_uri
        self.username = username
        self.password = password
        self.splunk_app = splunk_app

    def __delete_dashboard(self,dashboard_name:str):
        
        response = requests.delete(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views/{dashboard_name}',
                                verify=False,
                               
                                auth=(self.username, self.password))
        return response


    def delete_dashboard(self,dashboard_name:str):
        return self.__delete_dashboard(dashboard_name=dashboard_name)


    def delete_dashboard_list(self,dashboard_list:list):
        response_list=[]
        for dashboard_name in dashboard_list:
            reponse_list.append(self.delete_dashboard(dashboard_name=dashboard_name))
        return response_list

    def __get_dashboard(self, dashboard_name: str):
        params = (
            ('output_mode', 'json'),
        )
        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views/{dashboard_name}',
                                verify=False,
                                params=params,
                                auth=(self.username, self.password))
        return response

    def get_dashboard(self, dashboard_name: str):
        response = self.__get_dashboard(
            dashboard_name=dashboard_name
        )
        content = json.loads(response.content)
        xml=content['entry'][0]['content']['eai:data']
        acl=content['entry'][0]['acl']
        return xml, acl
        #return response

    def get_dashboard_list(self, title_regex=["**"]):
        '''returns a list object with alle the dashb'''

        splunk_search = f"""
        | rest/servicesNS/-/{self.splunk_app}/data/ui/views splunk_server=local
| table disabled title
        """
        for pattern in title_regex:
            splunk_search = f"""{splunk_search}
            | search title ="{pattern}"
            """
        print(splunk_search)
        data = {
            'search': splunk_search, 'output_mode': 'json'
        }
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/search/search/jobs/export',
                                 data=data,
                                 verify=False,
                                 auth=(self.username, self.password))

        text = response.text
        text_array = text.split('\n')
        _list = [json.loads(text_e)
                 for text_e in text_array if text_e is not '']
        _list = [e['result']['title'] for e in _list]
        # the fastest way to dedup a list https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists/7961425#7961425
        _list = list(dict.fromkeys(_list))
        return _list

    def __create_dashboard(self, dashboard_name: str, xml: str):

        params = (
            ('output_mode', 'json'),
        )
        dashboard_config = {
            'name': dashboard_name,
            'eai:data': xml
        }
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views',
                                 data=dashboard_config,
                                 verify=False,
                                 params=params,
                                 auth=(self.username, self.password))

        return response

    def create_dashboard(self, dashboard_name: str, xml: str, title:str=None, overwrite=False):

        exists_response=self.__get_dashboard(dashboard_name=dashboard_name)
        if exists_response.status_code==200:
            print(f"{dashboard_name} already exists.")
            
            if overwrite==False:
                return get_response_object(status_code=409)
            else:
                del_response=self.__delete_dashboard(dashboard_name=dashboard_name)
                print(f"{del_response.status_code} Deleted existing dashboard {dashboard_name}")
                if del_response.status_code!=200:
                    print("delete failed. check dashboard acl, permissions")
                    return get_response_object(status_code=409)



        if title:
            tree = ET.ElementTree(ET.fromstring(xml))
            root=tree.getroot()
            root.find('label').text=title
            xml=ET.tostring(root)

        response=self.__create_dashboard(dashboard_name,xml)
        return response

    def __update_dashboard(self, dashboard_name: str, xml: str):
        pass

    def update_dashboard(self, dashboard_name: str, xml: str):
        pass


    def update_navbar(self,xml:str):
        #experimental does not work yet. default.xml cannot be found for some reason
        navbar_config = {
            
            'eai:data': xml
        }
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/nav/default',
                                 data=navbar_config,
                                 verify=False,
                                
                                 auth=(self.username, self.password))

        return response


    def get_navbar(self):
        params = (
            ('output_mode', 'json'),
        )
        
        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/nav/default',
                                 params=params,
                                 verify=False,
                                
                                 auth=(self.username, self.password))

        content = json.loads(response.content)
        xml=content['entry'][0]['content']['eai:data']
        acl=content['entry'][0]['acl']
        return xml, acl


    def get_dashboard_acl(self, dashboard_name):
        params = (
            ('output_mode', 'json'),
        )
        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views/{dashboard_name}/acl',
                                 
                                 verify=False,
                                 params=params,
                                 auth=(self.username, self.password))

        return json.loads(response.content)['entry'][0]['acl']

    def change_dashboard_acl(self,dashboard_name, dashboard_acl_dict):

        
        response = requests.post(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views/{dashboard_name}/acl',
                                 verify=False,
                                 data=dashboard_acl_dict,
                                 auth=(self.username, self.password))
        print(f"{response.status_code}, while changing ACL of {dashboard_name}")                         
        return response


class SplunkAutomator():
    """This class can be used to build scripts to automate certain splunk tasks.

    The class needs to be initialized with the Splunk URL and a username and password.
    The splunk user needs to have admin rights

    

    Attributes:
        splunk_ui (str): the splunk URL.
        username (str): the splunk user username.
        password (str): the splunk user password.
        splunk_app (str): the splunk app (url name) under which alerts should be created.

    """

    def __init__(self, splunk_uri:str, username:str, password:str, splunk_app:str=None) -> None:
        
        self.alerts=SplunkAlertAutomator(splunk_uri, username, password, splunk_app)
        self.dashboards=SplunkDashboardAutomator(splunk_uri, username, password, splunk_app)

    def __repr__():
        pass
        


class SplunkMigrater():
    '''This class can be used to perform migrations from one splunk instance to another (Dashboards, Alerts, etc.)


    Attributes:
        from_splunk (SplunkAutomator): the Splunk from which we want to migrate things.
        to_splunk (SplunkAutomator): the Splunk to which we want to migrate things.
    '''

    def __init__(self,from_splunk:SplunkAutomator, to_splunk:SplunkAutomator) -> None:
        self.from_splunk=from_splunk
        self.to_splunk=to_splunk

    def set_splunk_environments(from_splunk:SplunkAutomator, to_splunk:SplunkAutomator)->None:
        self.from_splunk=from_splunk
        self.to_splunk=to_splunk

    def move_alert(self,alert_name:str,overwrite=False, alert_acl_dict=None):
        '''moves an alert from from_splunk to to_splunk'''
        alert_name, alert_configs,_=self.from_splunk.alerts.get_alert(alert_name)
        
        r_create=self.to_splunk.alerts.create_alert(alert_configs=alert_configs,overwrite=overwrite)
        
        r_acl=None
        if alert_acl_dict:
            r_acl=self.to_splunk.alerts.change_alert_acl(alert_name=alert_name, alert_acl_dict= alert_acl_dict)


        return r_create,r_acl

    def move_alert_list(self,alert_list:list,overwrite=False,alert_acl_dict=None):
        '''moves all alerts in the list from from_splunk to to_splunk'''
        response_list_move=[]
        response_list_acl=[]
        for alert_name in alert_list:
            r_move,r_acl=self.move_alert(alert_name=alert_name,overwrite=overwrite, alert_acl_dict= alert_acl_dict)
            response_list_move.append(r_move)
            response_list_acl.append(r_acl)

        return response_list_move,response_list_acl

    def move_dashboard(self, dashboard_name:str, overwrite:bool=False, dashboard_acl_dict:dict=None):
        '''moves an dash from from_splunk to to_splunk'''
        xml, _=self.from_splunk.dashboards.get_dashboard(dashboard_name=dashboard_name)
        
        r_create=self.to_splunk.dashboards.create_dashboard(dashboard_name=dashboard_name, xml=xml, overwrite=overwrite)
        #create_dashboard(self, dashboard_name: str, xml: str, title:str=None, overwrite=False):
        r_acl=None
        if dashboard_acl_dict and (r_create.status_code==201):
            r_acl=self.to_splunk.dashboards.change_dashboard_acl(dashboard_name=dashboard_name, dashboard_acl_dict= dashboard_acl_dict)


        return r_create,r_acl

    def move_dashboard_list(self, dashboard_list:list, overwrite:bool=False,dashboard_acl_dict:dict=None):
        '''moves all dashboards in the list from from_splunk to to_splunk'''
        response_list_move=[]
        response_list_acl=[]
        for dashboard_name in dashboard_list:
            r_move,r_acl=self.move_dashboard( dashboard_name=dashboard_name, overwrite=overwrite,dashboard_acl_dict= dashboard_acl_dict)
            response_list_move.append(r_move)
            response_list_acl.append(r_acl)

        return response_list_move,response_list_acl