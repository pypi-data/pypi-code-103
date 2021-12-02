import os
import requests

def config(API_Token):
    
    try:
        auth_status = (requests.get("http://13.76.30.220:4000/authorize", headers={"x-access-token": API_Token})).json()
        dir_path, _ = os.path.split(__file__)
        if auth_status['status'] == "SUCCESS":
            with open(dir_path + "/config_variables.py", "w") as config_file:
                config_file.write('API_TOKEN = "' + API_Token + '"\n')
        else:
            with open(dir_path + "/config_variables.py", "w") as config_file:
                config_file.write('API_TOKEN = None\n')
    
    except:
        auth_status = {}
        auth_status['status'] = "FAILURE"
        auth_status['response'] = "Failed to connect to the server"
            
    return auth_status
