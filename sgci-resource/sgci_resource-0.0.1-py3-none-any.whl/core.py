from github import Github
import requests
import json
import jmespath
import hashlib
import jsonschema
import warnings
import re
import copy
import os

class SCGICatalog():
    def __init__(self, **kwargs):
        self.schema_path = kwargs.get("schema", "https://raw.githubusercontent.com/SGCI/sgci-resource-inventory/master/schema/resources-schema.json")
        schema = requests.get(self.schema_path)
        self.schema = json.loads(schema.text)
        self.cache = kwargs.get("cache", True) 
        self.validate = kwargs.get("validate", True) 
        self.list_resources = {}
    
    def listResources(self, filter="", **kwargs):
        raise Exception("not implemented")

    def getResource(self, filter="", **kwargs):
        raise Exception("not implemented")
        
    def validateResource(self, resource):
        jsonschema.validate(instance=resource, schema=self.schema)
    
    def derefResource(self, obj, resources={}):
        if isinstance(obj, str):
            obj = json.loads(obj)
        else:
            obj = copy.deepcopy(obj)
        return self.recursivederef(obj, resources)
        
    def recursivederef(self, obj, resources={}):
        if isinstance(obj, dict):
            if "#ref" in obj:
                match = re.match("^\{([a-zA-Z][a-zA-Z0-9_\.]*)}#(.*)", obj["#ref"])
                if (match is not None):
                    if str(match[1]) in resources:
                        return jmespath.search(match[2], resources[match[1]])
                    else:
                        raise Exception(match[1] + " is an invalid Resource")
                else :
                    obj[i] = self.recursivederef(v, resources)
            else:
                for i,v in obj.items():
                    obj[i] = self.recursivederef(v,resources)
        elif isinstance(obj, list):
            for i,v in enumerate(obj):
                obj[i] = self.recursivederef(v, resources)
        return obj
    
    def hashKey(self, obj):
        d = {k:obj[k] for k in obj.keys() if not isinstance(obj[k],dict) and not isinstance(obj[k],list)}
        key = json.dumps(d, sort_keys = True)
        return hashlib.md5(key.encode()).digest().hex() 

    def searchPath(self, path, res):
        return jmespath.search(path, res)
    
    def mergeResources(self, resources):
        if len(resources) < 1:
            return {}
        elif len(resources) == 1:
            return resources[0]
        else:
            dct = {}
            for res in resources:
                for key in res.keys():
                    dct[key] = dct.get(key, res[key])
                for key in dct.keys():
                    if isinstance(dct[key], dict):
                        dct[key] = self.mergeResources([dct[key], res[key]])
                    elif isinstance(dct[key], list):
                        if key in res:
                            for elem in res[key]:
                                if isinstance(elem, dict):
                                    k1 = self.hashKey(elem)
                                    found = -1
                                    for ii, elem2 in enumerate(dct[key]):
                                        if k1 == self.hashKey(elem2):
                                            found = ii
                                    if found >= 0:
                                        dct[key][found] = self.mergeResources([dct[key][found], elem])
                                    else:
                                        dct[key].append(elem)
                                else:
                                    if elem not in dct[key]:
                                        dct[key].append(elem)
            return dct;
 
    
class SCGICatalogGithub(SCGICatalog):
    def __init__(self, **kwargs):  
        super(SCGICatalogGithub, self).__init__(**kwargs)
        if kwargs.get("token", None) is not None:
            self.github = Github(kwargs.get("token", None));      
        elif kwargs.get("user", None) is not None and  kwargs.get("password", None) is not None:
            self.github = Github(kwargs.get("user", None), kwargs.get("password", None));   
        else:
            raise Exception ("not a valid authentication Method")
        self.repo_path = kwargs.get("repo", "SGCI/sgci-resource-inventory") 
        try:
            self.github.get_user().name
        except Exception as e:
            raise e
        self.listResources(filter="")
            
    def listResources(self, filter="", **kwargs):
        if self.cache == True and len(self.list_resources) > 0:
            pass;
        else:
            self.repo = self.github.get_repo(self.repo_path)
            contents = self.repo.get_contents("data")
            self.list_resources = {
                c.path.replace("data/", "", 1).replace(".json", "", 1):None 
                for c in contents
            }
        return list(self.list_resources.keys())
    
    def getResource(self, resource, **kwargs):
        if self.cache == True and resource in self.list_resources and self.list_resources[resource] is not None:
            res = self.list_resources[resource]
        else:
            self.repo = self.github.get_repo(self.repo_path)
            content = self.repo.get_contents("data/"+resource+".json")
            try:
                self.list_resources[resource] = json.loads(content.decoded_content.decode())
                res = self.list_resources[resource]
            except Exception as e:
                raise e
        if self.validate:
            try:
                self.validateResource(res)
            except jsonschema.exceptions.ValidationError as e:
                warnings.warn(e.message)
            except Exception as e:
                raise e
        return res


    
class SCGICatalogXsede(SCGICatalog):
    def __init__(self, **kwargs):   
        super(SCGICatalogXsede, self).__init__(**kwargs)
        self.ws_path = kwargs.get("ws", "https://info.xsede.org/wh1/warehouse-views/v1/resources-sgci/v1.0.0")
        self.listResources(filter="")
        
    def listResources(self, filter="", **kwargs):
        if self.cache == True and len(self.list_resources) > 0:
            pass; 
        else:
            resources = requests.get(self.ws_path + '?format=json')
            resources = json.loads(resources.text)
            self.list_resources = {res["host"]:res for res in resources["results"]}
        return list(self.list_resources.keys())
    
    def getResource(self, resource, **kwargs):
        if resource in self.list_resources:
            res = self.list_resources[resource]
        else:
            raise Exception("Resource not found")
        if self.validate:
            try:
                self.validateResource(res)
            except jsonschema.exceptions.ValidationError as e:
                warnings.warn(e.message)
            except Exception as e:
                raise e
        return res


class SCGICatalogLocal(SCGICatalog):
    def __init__(self, **kwargs):  
        super(SCGICatalogLocal, self).__init__(**kwargs)
        self.folder_path = kwargs.get("folder", "./sgci-resource-inventory") 
        self.listResources(filter="")
            
    def listResources(self, filter="", **kwargs):
        if self.cache == True and len(self.list_resources) > 0:
            pass;
        else:
            for file in os.listdir(self.folder_path):
                if file.endswith(".json"):
                    self.list_resources[file.replace(".json", "")] = None        
        return list(self.list_resources.keys())
    
    def getResource(self, resource, **kwargs):
        if self.cache == True and resource in self.list_resources and self.list_resources[resource] is not None:
            res = self.list_resources[resource]
        else:
            try:
                f = open(self.folder_path+"/"+resource+".json" , "r")
                content = f.read()
            except:
                raise Exception("Resource not found")                
            try:
                self.list_resources[resource] = json.loads(content)
                res = self.list_resources[resource]
            except Exception as e:
                raise e
        if self.validate:
            try:
                self.validateResource(res)
            except jsonschema.exceptions.ValidationError as e:
                warnings.warn(e.message)
            except Exception as e:
                raise e
        return res
