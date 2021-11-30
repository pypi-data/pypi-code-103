# -*- coding:utf-8 -*-

import logging
import prance
from osc_openapi_framework import schema


def parse(path):
    content = prance.ResolvingParser(
        path, backend='openapi-spec-validator'
    ).specification
    return schema.API(content['info'], parse_calls(content['paths'],),
                      content['security'], content['servers'])


def parse_calls(calls):
    result = {}
    for k, v in calls.items():
        call_name = k[1:]
        http_verb = 'post' if 'post' in v.keys() else 'get'
        try:
            if 'requestBody' in v[http_verb]:
                request_content = v[http_verb]['requestBody']['content']
                request_structure = (request_content['application/json']['schema']
                                     if 'application/json'in request_content
                                     else request_content)
                
                try:
                    resp_content = v[http_verb]['responses']['200']['content']
                except KeyError:
                    resp_content = {}
                
                resp_structure = (resp_content['application/json']['schema']
                                  if 'application/json' in resp_content
                                  else resp_content)
                result[call_name] = schema.Call(
                    call_name,
                    parse_params(request_structure['properties'],
                                 'in', call_name)
                    if request_structure else {},
                    parse_params(resp_structure['properties']
                                 if 'properties' in resp_structure
                                 else {'result':  resp_structure},
                                 'out', call_name)
                    if resp_structure else {},
                    (request_structure.get('required', []))
                    if request_structure else [],
                    next((x for x in v[http_verb].get('tags', [])), ''),
                    'security' in v[http_verb] and not v[http_verb]['security'],
                    v[http_verb]['requestBody']['description']
                    if 'description' in v[http_verb]['requestBody']
                    else v[http_verb].get('description', 'NO DESC'),
                    v[http_verb]['responses']['200'].get('description', 'NO DESC')
                    if '200' in v[http_verb]['responses']
                    else 'NO DESC',
                    http_verb
                )
        except:
            logging.exception("Error while parsing call {}:".format(call_name))
            continue
    return result


def parse_params(params, *args, **kwargs):
    result = {}
    for k, v in params.items():
        try:
            if v:
                value = (
                    parse_array if v['type'] == 'array' else
                    parse_object if v['type'] == 'object' else
                    parse_terminal
                )(k, v, *args, **kwargs)
                if value is not None:
                    result[k] = value
        except:
            logging.error("Error while parsing param {}.".format(k))
            raise
    return result


def parse_object(name, param, *args, **kwargs):
    return schema.ObjectField(
        parse_params(param['properties']
                     if 'properties' in param
                     else {},  # TODO(GMT): How to manage additionalProperties?
                     *args, **kwargs),
        name, 'object', *args, description=param.get('description', 'TODO_OBJ')
    )


def parse_array(name, param, *args, **kwargs):
    if 'type' in param['items']:
        return schema.ArrayField((
            parse_object if param['items']['type'] == 'object' or
                            param['items']['type'] == 'array'  # TODO(GMT): Workaround
            else parse_terminal
        )(name, param['items'], *args, **kwargs), name, 'array', *args,
                                 description=param.get('description', 'TODO_ARRAY'))
    else:
        return None


def parse_terminal(name, param, *args, required=None, **kwargs):
    return schema.TerminalField(
        name, param['type'], *args,
        description=param.get('description', 'TODO_TERM'),
        default=param.get('default'),
        fieldformat=param.get('format')
    )
