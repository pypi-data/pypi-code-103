from flask_jwt_extended import  decode_token
from flask import request
from functools import wraps

def role_required(required_roles):
    '''
        Takes in an array of UPPERCASED roles that reflect the permissions needed to access a particular route
        
        Eg. ['USER', 'ADMIN', 'SUPERUSER']
        It then compares the roles passed with the user role found in the JWT token. If the required role matches to any of the user roles,
        access is grant. 
    '''
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            encoded_jwt  = request.headers.get('Authorization').split(" ")[1]
            for role in decode_token(encoded_jwt)['sub']['roles']:
                if role in required_roles:
                    return func(*args, **kwargs)
            raise ValueError("User does not have the required permissions")

        return wrapper
    return decorator