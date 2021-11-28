import os

import requests
import json
import pandas as pd
import logging
import time
import io

#from fs.memoryfs import MemoryFS
from .json_to_table import JsonToTable
log = logging.getLogger(__name__)

class BailamAPI():
    # Balaim API to generate code from dample data
    """
    The API can be use to send the source and target data to tge Bailam server in order to initiate the learning
    Once the learning is done the code generate can be retrieve or and use in python

            :param link_name: Name of the Smart link to be created
            :param source: Datafrane with the source data
            :param target: Dataframe with target data
            :param system_link_pk: pk of the system link to retrieve an existing Systemlink
            :param token: security token for your user
    """
    token = '18ae4d817a80c0bbe0e4fe67d492075bca7c1363' #test_public user
    protocol = 'https://'
    base_url = 'app.bailam.com'
    systemlink_pk = 0
    local_map_function = None
    tmp_folder = 'tmp/'
    remove_tmp = True
    tmp_files = []
    def __init__(self,link_name=None,source=None, target=None,system_link_pk=None,token=None):

        if token is not None :
            self.token = token
        if system_link_pk is not None:
            self.systemlink_pk=system_link_pk
        elif source is not None  and target is not None :
            self.systemlink_pk = self.create_systemlink(link_name=link_name,source=source,target=target)
        else:
            self.systemlink_pk =0

    def request(self,rtype="GET",end_point=None,data=None,
                files=None,headers=None,sleep=1,retry = 3,good_status_limit=400):
        url = f"{self.protocol}{self.base_url}{end_point}"
        if headers is None :
            headers = {
             'Authorization': 'token '+self.token
            }
        nbtry = 0
        while nbtry < retry :
            response = requests.request(rtype, url, headers=headers, data=data, files=files)
            if response.status_code < good_status_limit :
                return response
            time.sleep(sleep)
            nbtry +=1

        if response.status_code >= 400 :
            raise ValueError(url + str(response))
        else :
            raise TimeoutError(url+str(response))


    def create_systemlink_from_files(self,link_name,source_file=None,target_file=None,learning_env={},):
        """
            Create system link from files
        """
        url = "/smartmap/api/smart-link/create-one-step/"

        payload = {'link_name': link_name }



        files = [
            ('source_scenario_data_file', open(source_file, 'rb')),
            ('target_scenario_data_file', open(target_file, 'rb')),

        ]
        headers = {
             'Authorization': 'token '+self.token
            }

        response = self.request("POST", url, headers=headers, data=payload, files=files)

        r = json.loads(response.text.encode('utf8'))
        systemlink_id = r['id']

        self.systemlink_pk = systemlink_id

        return systemlink_id

    def register_tmp_file(self,filename):
        os.makedirs(self.tmp_folder, exist_ok=True)
        full_filename = os.path.join( self.tmp_folder,filename)
        self.tmp_files.append(full_filename)
        return full_filename
    def clean_tmp(self):
        if self.remove_tmp :
            for f in self.tmp_files :
                try :
                        os.remove(f)
                except FileNotFoundError :
                    log.warning(f"for {f} not in tmp directory anymore ")
            self.tmp_files =[] #TODO remove one by one

    def create_systemlink(self, link_name, source, target, learning_env={},
                                  index_source=False, index_target =False ):
        """
            Create system link from files
        """
        tmp_files = []
        if isinstance(source,pd.DataFrame)  :
            #output = io.BytesIO()
            #writer = pd.ExcelWriter(output, engine='xlsxwriter')
            #source.to_excel(writer)
            #writer.save()
            #output.seek(0)
            #workbook = output.read()
            source_file= self.register_tmp_file(   link_name + '_source.xlsx')
            source.to_excel(source_file, index=index_source)
        elif isinstance(source,dict) or isinstance(source,list) :
            source_file =self.register_tmp_file(  link_name + '_source.json')
            out_file = open(source_file, "w")
            json.dump(source, out_file)
            out_file.close()
        else :
           source_file = source
        if isinstance(target,pd.DataFrame)  :
            target_file= self.register_tmp_file( link_name + '_target.xlsx')
            target.to_excel(target_file ,index=index_target)
        else :
            target_file = target
        url = "/smartmap/api/smart-link/create-one-step/"

        payload = {'link_name': link_name}

        files = [
            ('source_scenario_data_file', open(source_file, 'rb')),
            ('target_scenario_data_file', open(target_file, 'rb')),

        ]
        headers = {
            'Authorization': 'token ' + self.token
        }

        response = self.request("POST", url, headers=headers, data=payload, files=files)

        r = json.loads(response.text.encode('utf8'))
        systemlink_id = r['id']

        self.systemlink_pk = systemlink_id

        self.clean_tmp()

        return systemlink_id


    def get_systemlink_result(self):
        headers = {
            'Authorization': 'token ' + self.token
        }

        url = f"/smartmap/api/smart-link/{self.systemlink_pk}/result-transformation"
        response = self.request("GET", url, headers=headers, )

        tab_res = pd.DataFrame.from_dict(
            json.loads(response.text)['result_transformation_using_pycode'],orient='index')


        return tab_res


    def set_and_get_systemlink_id(self,system_link_id=None):
        if system_link_id is not None :
            self.systemlink_pk = system_link_id
        return  self.systemlink_pk

    def map_new_file(self,file,system_link_pk=None):
        slpk = self.set_and_get_systemlink_id(system_link_pk)
        url = f"/smartmap/api/mappings/?smart-link-pk={slpk}"

        payload = {'process_type': 'MAP'}
        files = [
            ('source_file', open(file, 'rb'))
            ]
        headers = {
             'Authorization': 'token '+self.token
            }

        response = self.request("POST", url, headers=headers, data=payload, files=files,retry=1)

        r = json.loads(response.text.encode('utf8'))
        process_id = r['id']

        url_get = f"/smartmap/api/mappings/{process_id}/file/?type=json"
        response_get = self.request("GET", url_get, headers=headers,retry=5)
        r_get = json.loads(response_get.text.encode('utf8'))
        tab_res = pd.DataFrame.from_dict(r_get)
        return tab_res

    def get_file_mapping_result(self,mapping_pk):
        url = "/{mapping_pk}/file/?type=json"

        payload = {}
        headers = {
         'Authorization': 'token '+self.token
        }
        response = self.request("GET", url, headers=headers, data = payload)
        tab_res = pd.DataFrame.from_dict(json.loads(response.text))

        return tab_res


    def def_mapping_function(self,systemlink_pk=None):

        system_link_pk=self.set_and_get_systemlink_id(systemlink_pk)
        code_py = self.get_mapping_function_code(system_link_pk)


        exec(code_py)

        new_f = eval("transform")
        self.local_map_function = new_f
        return new_f

    def map(self,df,systemlink_pk=None):
        if systemlink_pk is not None :
            f = self.def_mapping_function(systemlink_pk)
        elif  self.local_map_function is None and self.systemlink_pk is not None:
            f = self.def_mapping_function(self.systemlink_pk)
        elif self.local_map_function is not None :
            f = self.local_map_function
        else :
            raise ValueError("the systemlink is not set yet you need to pas the systemlink id for the first use")

        return f(df)


    def get_mapping_function_code(self, systemlink_pk=None,language="py"):

        slpk = self.set_and_get_systemlink_id(systemlink_pk)

        url_for_py = f"/smartmap/api/smart-link/{slpk}/code/?language={language}"

        payload = {}
        headers = {
            'Authorization': 'token ' + self.token
        }

        response_py = self.request("GET", url_for_py, headers=headers, data=payload)
        if response_py.status_code == 404:
            raise KeyError(f"error 404 for system link {systemlink_pk}")
        r_py = json.loads(response_py.text.encode('utf8'))

        return r_py['code']


