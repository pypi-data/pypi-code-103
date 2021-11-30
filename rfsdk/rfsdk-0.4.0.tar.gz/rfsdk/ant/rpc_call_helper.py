import json

try:
    from google.protobuf import json_format

    SUPPORT_PY_PROTOBUF = True
except Exception as e:
    SUPPORT_PY_PROTOBUF = False

import pyant


def call(service_name, method, data, op=pyant.Option.default_instance(), ep=pyant.Endpoint.default_instance()):
    if isinstance(data, str):
        msg_json = data
    elif isinstance(data, dict):
        msg_json = json.dumps(data)
    elif SUPPORT_PY_PROTOBUF and isinstance(data, google.protobuf.message.Message):
        msg_json = json_format.MessageToJson(
            data, preserving_proto_field_name=True, use_integers_for_enums=True)
    else:
        return -1, 'not supported data type'

    ret, msg = pyant.json_call_wait(service_name, method, msg_json, op, ep)
    if 0 == ret:
        msg = json.loads(msg)
    return ret, msg


def call_mf(service_name, method, data, op=pyant.Option.default_instance(), ep=pyant.Endpoint.default_instance()):
    if isinstance(data, str):
        msg_json = data
    elif isinstance(data, dict):
        msg_json = json.dumps(data)
    elif SUPPORT_PY_PROTOBUF and isinstance(data, google.protobuf.message.Message):
        msg_json = json_format.MessageToJson(
            data, preserving_proto_field_name=True, use_integers_for_enums=True)
    else:
        return -1, 'not supported data type'

    ret, msg = pyant.json_call_mf_wait(service_name, method, msg_json, op, ep)
    if ret == 0:
        for i in range(len(msg)):
            msg[i] = json.loads(msg[i])
    return ret, msg


def async_call(service_name, method, data, op=pyant.Option.default_instance(), ep=pyant.Endpoint.default_instance()):
    if isinstance(data, str):
        msg_json = data
    elif isinstance(data, dict):
        msg_json = json.dumps(data)
    elif SUPPORT_PY_PROTOBUF and isinstance(data, google.protobuf.message.Message):
        msg_json = json_format.MessageToJson(
            data, preserving_proto_field_name=True, use_integers_for_enums=True)
    else:
        raise Exception('not supported data type')

    return pyant.json_call(service_name, method, msg_json, op, ep)
