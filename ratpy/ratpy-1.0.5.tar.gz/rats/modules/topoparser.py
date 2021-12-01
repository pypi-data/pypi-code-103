import platform
import pathlib
from bs4 import BeautifulSoup as bs
from rats.modules.RATS_CONFIG import LLCEDB

if platform.system() == 'Windows':
    topopath = '\\topo\\'
else:
    topopath = '/topo/'
packagepath = pathlib.Path(__file__).parent.parent.resolve()


def extractscale(netid, edblist):
    edbs = [i for i in edblist] # stop this modifying core attribute of class
    # need to organically identify the topo file
    import os
    for filename in os.listdir(str(packagepath) + topopath):
        if 'NETWORK' in filename and 'xml' in filename:
            topofile = filename
        else:
            f'{filename} checked'

    with open(str(packagepath) + topopath + topofile, 'r') as f:
        content = f.readlines()
        content = "".join(content)
        soup = bs(content, 'lxml')

    device = soup.find('de:device', {'netid': netid})
    board = device['instancename']
    description = {}
    units = {}
    scalingfactor = {}
    minimum = {}
    maximum = {}
    bytesdict = {}

    with open(str(packagepath) + topopath + f'DEVICE_{device["type"]}_{device["variant"]}.xml', 'r') as f:
        content = f.readlines()
        content = "".join(content)
        soup = bs(content, 'lxml')

    for edb in edbs:
        addr42 = soup.find('ep:interfaceaddress', {'addr': '42'})
        data = addr42.find('is:setting', {'id': edb})
        description[edb] = data['description']
        units[edb] = data['unit']
        minimum[edb] = int(data['minvalue'])
        maximum[edb] = int(data['maxvalue'])
        bits = int(data['dataformat'].split('Q')[1]) + 1 # if q15, will be interpreted as 16 bit number, for example
        res = 2 ** bits
        bytesdict[edb] = int(bits/4)

        '''
        apply this with following logic; 
        if min < max;
            scaled data = min + data*res
        if min > max;
            scaled data = min + (data * -res)
        '''
        scalingfactor[edb] = abs((int(data['maxvalue']) - int(data['minvalue']))) / res
        if int(data['maxvalue']) < int(data['minvalue']):
            # invert this so that 'min' + scaling factor will decrement
            scalingfactor[int(f"{edb}")] = (scalingfactor[int(f"{edb}")]) * -1

    scalingfactors = dict(descriptions=description, units=units, minimum=minimum, maximum=maximum,
                          scalingfactor=scalingfactor, bytes=bytesdict)

    return scalingfactors, board #maybe split these out in the class...


def testcase(netid, e):
    output = extractscale(netid, e)
    return output



