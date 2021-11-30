import re
import logging
import csv
import json
from os import path, listdir

def add_defaultsuffix(file, suffix) :
    if not re.match(f'.+\.{suffix}',file) :
        file += '.'+suffix
    return file


def toggle_mockapi_file(file,comment=False) :
    if not comment :
        logging.info(f"Uncomment 'mockapi' from script: {file}")
    else :
        logging.info(f"Comment 'mockapi' from script: {file}")
    script = ''
    with open(file,'r') as fp:
        line = fp.readline()
        while(line) :
            if comment :
                # from utils.mock_di_api import mock_api
                if re.match('from\s+utils.mock_di_api\s+import\s+mock_api',line) :
                    line = re.sub('from\s+utils.mock_di_api\s+import\s+mock_api','#from utils.mock_di_api import mock_api',line)
                # api = mock_api
                if re.match('api\s*=\s*mock_api',line) : #api = mock_api(__file__)
                    line = re.sub('api\s*=\s*mock_api','#api = mock_api',line)
                # from diadmin.dimockapi.mock_api import mock_api
                if re.match('from\s+diadmin.dimockapi.mock_api\s+import\s+mock_api',line) :
                    line = re.sub('from\s+diadmin.dimockapi.mock_api\s+import\s+mock_api','#from diadmin.dimockapi.mock_api import mock_api',line)
            else:
                if re.match('#from\s+utils.mock_di_api\s+import\s+mock_api',line) :
                    line = re.sub('#from\s+utils.mock_di_api\s+import\s+mock_api','from utils.mock_di_api import mock_api',line)
                if re.match('#api\s*=\s*mock_api',line) : #api = mock_api(__file__)
                    line = re.sub('#api\s*=\s*mock_api','api = mock_api',line)
                # from diadmin.dimockapi.mock_api import mock_api
                if re.match('#from\s+diadmin.dimockapi.mock_api\s+import\s+mock_api',line) :
                    line = re.sub('#from\s+diadmin.dimockapi.mock_api\s+import\s+mock_api','from diadmin.dimockapi.mock_api import mock_api',line)

            script += line
            line = fp.readline()
    with open(file,'w') as fp :
        fp.write(script)

def toggle_mockapi(dir,comment) :
    logging.info(f'Folder: {dir}')
    if path.isfile(path.join(dir,'operator.json')) :
        script_name = get_script_name(dir)
        toggle_mockapi_file(path.join(dir,script_name),comment)
        return None
    for sd in listdir(dir) :
        if path.isdir(path.join(dir,sd)) :
            toggle_mockapi(path.join(dir,sd),comment)

def get_script_name(dir) :
    with open(path.join(dir,'operator.json')) as jf :
        opjson = json.load(jf)
    script_name = opjson['config']['script'][7:]
    logging.info(f"Script: {script_name}")
    return script_name

# Read csv userlist
# format: username, password, name
def read_userlist(filename) :
    users = list()
    with open(path.join('users',filename),mode='r',newline='\n') as csvfile :
        csvreader = csv.reader(csvfile,delimiter = ',')
        for line in csvreader:
            if line[0][0] == '#' :
                continue
            users.append({'tenant':line[0],'user':line[1],'name':line[2],'pwd':line[3],'role':line[4]})
    return users

def write_userlist(userlist,filename) :
    with open(path.join('users',filename),mode='w',newline='\n') as csvfile :
        for u in userlist:
            csvfile.write(f"{u['tenant']},{u['user']},{u['name']},{u['pwd']},{u['role']}\n")


def mksubdir(parentdir,dir) :
    newdir = path.join(parentdir,dir)
    if not path.isdir(newdir) :
        logging.info(f"Make directory: {newdir}")
        mkdir(newdir)
    return newdir