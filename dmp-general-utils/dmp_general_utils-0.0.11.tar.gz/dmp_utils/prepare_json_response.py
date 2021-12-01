from flask import jsonify


def prepare_json_response(sms, success, data=None, code=200):
    json_object = {'data': data} if data is not None else {}
    return jsonify({
        'message': sms,
        'success': success,
        **json_object
    }), code
