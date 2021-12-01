# -*- coding: utf-8 -*-
import logging
import time
from . import amo_interaction
logger = logging.getLogger(__name__)


# return all the data to the contact by contact id
def get_contact_from_id(contact_id):
    # prepare and send the request
    res, status_code = amo_interaction.request('get', 'v2/contacts', params={'id': contact_id})
    if status_code == 200:
        return res.json()['_embedded']['items'][0]
    else:
        return None


def get_lead_from_id(lead_id):
    # prepare and send the request
    res, status_code = amo_interaction.request('get', 'v2/leads', params={'id': lead_id})
    if status_code == 200:
        return res.json()['_embedded']['items'][0]
    else:
        return None


def update_lead(lead_id, status_id, name, update_data=None):
    """
    Updating leads: the parameters “id”, “updated_at”, “status_id”, “name” ‘are required
    valid format for update_data could be:
        data = {
            'custom_fields': [{
                    'id': 601451,  # donation source, clubs
                    'values': [{'value': 'Клубы'}],
                },
                {
                    'id': 609813,  # donation source, which club
                    'values': [{'value': amo_club_name}],
                }]
        }
    """
    # prepare and send the request
    params = {'type': 'json'}
    data = {'update': [{
                  'id': lead_id,
                  'name': name,
                  'updated_at': int(time.time()),
                  'status_id': status_id
                }]}
    if update_data is not None:
        data['update'][0].update(update_data)
    res, status_code = amo_interaction.request('post', 'v2/leads', params=params, data=data)

    return res, status_code


def update_contact(contact_id, update_data=None):
    """
    """
    data = {'update': [{
        'id': contact_id,
        'updated_at': int(time.time())}]}

    if update_data is not None:
        data['update'][0].update(update_data)
    res, status_code = amo_interaction.request('post', 'v2/contacts', data=data)

    logger.info('contact with id updated: {}'.format(contact_id))

    return res, status_code


def add_delete_tag_to_entities(entity_type, entity_ids):
    # entity_type:leads|contacts|companies|customers
    if not isinstance(entity_ids, list):
        entity_ids = [entity_ids]
    data = list()

    for entity_id in entity_ids:
        data.append({'id': entity_id, '_embedded': {'tags': [{'id': 332311}]}})

    res, status_code = amo_interaction.request('patch', f'v4/{entity_type}', data=data)
    return res, status_code


def write_tags_to_entity(tags_list, entity_type, entity_id):
    # entity_type:leads|contacts|companies|customers
    data = {'id': entity_id,
            '_embedded': {'tags': tags_list}}

    res, status_code = amo_interaction.request('patch', f'v4/{entity_type}', data=data)
    return res, status_code


def link_entity(entity_id, entity_type, to_entity_ids, to_entity_type):
    # entity_type:leads|contacts|companies|customers

    data = list()
    for to_entity_id in to_entity_ids:
        data.append({'to_entity_id': to_entity_id,
                     'to_entity_type': to_entity_type,
                     'metadata': {'is_main': True}})

    res, status_code = amo_interaction.request('post', 'v4/{}/{}/link'.format(entity_type, entity_id), data=data)
    return res, status_code


def unlink_entity(entity_id, entity_type, to_entity_ids, to_entity_type):
    # entity_type:leads|contacts|companies|customers

    data = list()
    for to_entity_id in to_entity_ids:
        data.append({'to_entity_id': to_entity_id,
                     'to_entity_type': to_entity_type,
                     'metadata': {'is_main': True}})

    res, status_code = amo_interaction.request('post', 'v4/{}/{}/unlink'.format(entity_type, entity_id), data=data)
    return res, status_code


def get_pipelines():
    res, status_code = amo_interaction.request('get', 'v4/leads/pipelines')
    data = list()
    if status_code == 200:
        data = res.json()['_embedded']['pipelines']
    return data


def add_lead(name, status_id, pipeline_id, update_data=None):
    data = {'add': [{
        'name': name,
        'status_id': status_id,
        'pipeline_id': pipeline_id
    }]}
    if update_data is not None:
        data['add'][0].update(update_data)

    res, status_code = amo_interaction.request('post', 'v2/leads', data=data)

    new_lead = res.json()['_embedded']['items'][0]
    logger.info('lead with id added: {}'.format(new_lead['id']))

    return new_lead


def add_contact(name, update_data=None):
    # prepare and send the request
    data = {'add': [{
        'name': name
    }]}
    if update_data is not None:
        data['add'][0].update(update_data)

    res, status_code = amo_interaction.request('post', 'v2/contacts', data=data)

    new_contact = res.json()['_embedded']['items'][0]
    logger.info('contact with id added: {}'.format(new_contact['id']))

    return new_contact


def get_entity_by_id(entity_type, entity_id, with_str=None):
    # entity_type:leads|contacts|companies|customers
    if with_str is not None:
        params = {'with': with_str}
    else:
        params = None

    res, status_code = amo_interaction.request('get', 'v4/{}/{}'.format(entity_type, entity_id), params=params)
    if status_code == 200:
        entity = res.json()
    else:
        entity = None
    return entity, status_code


def get_all_entities(states_or_id_list, entity_type='contact', search_by='id', max_runs=20, limit_rows=500):
    all_entities = []
    logger.info(f'collecting all {entity_type}')

    if search_by not in ['id', 'status']:
        logger.error('only id or status is allowed')
        return
    if entity_type not in ['lead', 'contact']:
        logger.error('only contact or lead is allowed')
        return

    # create query string
    query_string = '?'
    for cid in states_or_id_list:
        query_string += search_by + '[]=' + str(cid) + '&'
    query_string = query_string[:-1]

    url = None
    if entity_type == 'contact':
        url = 'v2/contacts' + query_string
    elif entity_type == 'lead':
        url = 'v2/leads' + query_string

    total = 0
    run = 0
    while True:
        params = {'limit_rows': limit_rows,
                  'limit_offset': limit_rows * run,
                  'entity': entity_type,
                  'with': 'catalog_elements_links'}
        res, status_code = amo_interaction.request('get', url, params=params)

        time.sleep(1./7)

        if status_code == 200:
            data = res.json()
            entities = data['_embedded']['items']
        elif status_code == 204:
            entities = []
        else:
            logger.error('error' + str(res.status_code))
            break

        all_entities += entities
        total = len(all_entities)

        logger.info(f'{run}: total entities {total}')
        run += 1

        if len(entities) < limit_rows:
            break

        if run == max_runs:
            logger.info('got max runs! break')
            break

    logger.info('ready')
    logger.info(f'total entities {total}')
    return all_entities


def get_all_costum_fields(entity='leads'):
    params = {'limit': 500}
    res, status_code = amo_interaction.request('get', f'v4/{entity}/custom_fields', params=params)
    return res.json()['_embedded']['custom_fields']


def get_costum_field(field_id, entity='leads'):
    res, status_code = amo_interaction.request('get', f'v4/{entity}/custom_fields/{field_id}')
    return res.json()


def add_note_to_entity(entity_id, note, note_type='common', entity_type='leads'):
    # POST /api/v4/{entity_type}/{entity_id}/notes
    data = [{
        "entity_id": entity_id,
        "note_type": note_type,
        "params": {
            "text": note
        }}]

    print(data)
    res, status_code = amo_interaction.request('post', f"v4/{entity_type}/notes", data=data)
    return res.json(), status_code
