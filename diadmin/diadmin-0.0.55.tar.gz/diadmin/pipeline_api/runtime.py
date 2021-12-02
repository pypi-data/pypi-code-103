import logging
import copy
import time
from datetime import datetime


from urllib.parse import urljoin


import requests
import json
import yaml

start_template = {
    "src": "",
    "name": "",
    "executionType": "flow",
    "configurationSubstitutions": {},
    #"async": False
}

def get_graphs(connection) :
    restapi = "/runtime/graphs"
    url = connection['url'] + restapi
    logging.debug(f'Get runtime graphs URL: {url}')
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    resp = requests.get(url, headers=headers, auth=connection['auth'],verify=True)

    if resp.status_code != 200 :
        logging.error("Could not get runtime graphs!")
        return None

    rdata = json.loads(resp.text)
    data = dict()
    for r in rdata :
        #started = datetime.fromtimestamp(r['started']).strftime('%Y-%m-%d %H:%M:%S') if r['started'] >0  else '-'
        #submitted = datetime.fromtimestamp(r['submitted']).strftime('%Y-%m-%d %H:%M:%S') if r['submitted'] > 0 else '-'
        #stopped = datetime.fromtimestamp(r['stopped']).strftime('%Y-%m-%d %H:%M:%S') if r['stopped'] > 0 else '-'
        data[r['handle']] = {'pipeline':r['src'],'name':r['name'],'status': r['status'],
                             'submitted': r['submitted'],'started': r['started'],'stopped': r['stopped']}

    return data


def start_graph(connection,pipeline,pipeline_config) :

    params = copy.deepcopy(start_template)

    restapi = "/runtime/graphs"
    url = connection['url'] + restapi
    logging.debug(f'Start graph: {pipeline}')
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    params['src'] = pipeline
    cname = '-'.join(pipeline_config.values())
    params['name'] = 'Batch-'+cname
    params['configurationSubstitutions'] = pipeline_config
    r = requests.post(url, headers=headers, auth=connection['auth'], data = json.dumps(params))

    if r.status_code != 200:
        logging.error(f"Pipeline could not be started: {pipeline} - {r.status_code}\n{r.text}")
        return None

    r = json.loads(r.text)
    return {'pipeline': r['src'], 'name': r['name'],'user': r['user'],'tenant': r['tenant'],
            'status': r['status'],'config':r['configurationSubstitutions'],'handle':r['handle'],
            'submitted': r['submitted'],'started': r['started'],'stopped': r['stopped']}


def start_batch(connection,pipelines,max_procs = 2,sleep_time = 2 ) :

    processing = True
    num_procs = 0
    batch_index = 0
    procs =dict()
    while(processing) :
        # If all pipelines have been processed stop process
        if batch_index == len(pipelines):
            processing = False
            break
        # If there available resources start new pipeline
        if num_procs < max_procs :
            rec = start_graph(connection,pipelines[batch_index]['pipeline'],pipelines[batch_index]['configuration'])
            if rec  :
                logging.info(f"{batch_index} - Pipeline started: {rec['name']}")
                rec['batch_index'] = batch_index
                procs[rec['handle']] = rec
                num_procs +=1
            batch_index +=1  # in case of failing start of pipeline - it is skipped

        # Check runtime graphs for changes, update procs and free up proc resources
        runtime_graphs = get_graphs(connection)
        for h,rg in runtime_graphs.items():
            # filter runtime graphs
            if (not h in procs.keys()) or (procs[h]['status'] in ['dead','completed']) :
                continue
            # update procs
            logging.info(f"Check for update: {h}")
            procs[h]['status'] = rg['status']
            procs[h]['submitted'] = rg['submitted']
            procs[h]['started'] = rg['started']
            procs[h]['stopped'] = rg['stopped']

            if rg['status'] in ['dead','completed'] :
                num_procs -=1
                logging.info(f"Pipeline stopped: {rg['name']} -  {rg['status']}")
                logging.info(f"New proc resource available: {num_procs}/{max_procs}")

        time.sleep(sleep_time)

    # Wait until all processes are complete
    running = True
    while(running) :
        runtime_graphs = get_graphs(connection)
        running = False
        for h,rg in runtime_graphs.items():
            # filter runtime graphs
            if (not h in procs.keys()) or (procs[h]['status'] in ['dead','completed']) :
                continue
            # update procs
            logging.info(f"Check for update: {h}")
            procs[h]['status'] = rg['status']
            procs[h]['submitted'] = rg['submitted']
            procs[h]['started'] = rg['started']
            procs[h]['stopped'] = rg['stopped']

            if not rg['status'] in ['dead','completed']:
                running = True

        time.sleep(sleep_time)

    return procs


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    with open('config_demo.yaml') as yamls:
        params = yaml.safe_load(yamls)

    conn = {'url': urljoin(params['URL'] , '/app/pipeline-modeler/service'),
            'auth': (params['TENANT'] + '\\' + params['USER'], params['PWD'])}




    pipelines1 = [{ 'pipeline':'utils.conf_datagen', 'configuration':{'name':'extstart-1'}}]
    pipelines2 = [{ 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS-1'}},
                  { 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS2-2'}}]
    pipelines4 = [{ 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS-1'}},
                  { 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS2-2'}},
                  { 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS2-3'}},
                  { 'pipeline':'utils.conf_datagen', 'configuration':{'name':'BS2-4'}}]


    procs = start_batch(conn,pipelines=pipelines4)

    print(json.dumps(procs,indent=4))