from flask import jsonify, make_response


def success_ok():
    """Retorna un mensaje de exito"""
    return make_response(jsonify({"message": "success"}), 200)


def not_found(item=''):
    """Retorna un mensaje de no encontrado"""
    return make_response(jsonify({"message": "{} not found".format(item)}), 404)


def error_message(message):
    """Retorna un mensaje de error"""
    return make_response(jsonify({"message": message}), 406)


def error_params_required(params=[]):
    """
    Recibe un array con los parametros faltantes
    Retorna un mensaje con los parametros faltantes
    """
    message = {}
    for param in params:
        message[param] = 'Required field not found'
    return make_response(jsonify({"message": message}), 422)
