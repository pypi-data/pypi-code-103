import requests
import warnings
#import pandas as pd
import json
warnings.filterwarnings("ignore")


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

    def __get_dashboard(self,dashboard_name:str):
        params = (
            ('output_mode', 'json'),
        )
        response = requests.get(f'{self.splunk_uri}:8089/servicesNS/{self.username}/{self.splunk_app}/data/ui/views/{dashboard_name}',
                                   verify=False,
                                   params=params,                                  
                                   auth=(self.username, self.password))
        return response

    def get_dashboard(self,dashboard_name:str):
        response=self.__get_dashboard(
            dashboard_name=dashboard_name
        )
        payload=json.loads(response.content)
        xml=payload['content']['eai:data']
        acl=payload['acl']
        return xml, acl

    def get_dashboard_list(self,title_regex=["**"]):
        '''returns a list object with alle the dashb'''

        splunk_search=f"""
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

        text=response.text
        text_array=text.split('\n')
        _list=[json.loads(text_e) for text_e in text_array if text_e is not '']
        _list=[e['result']['title'] for e in _list] 
        _list=list(dict.fromkeys(_list))#the fastest way to dedup a list https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists/7961425#7961425
        return _list


    def __update_dashboard(self, dashboard_name:str, xml:str):
        pass

    def update_dashboard(self, dashboard_name:str, xml:str):
        pass



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

    def move_dashboard(self):
        pass

    def move_dashboard_list(self):
        pass