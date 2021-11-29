import os
def prepare_sql_data(data):
    sql_data = {
        'query': data['args'][data['config']['argsIndex']],
        'poSessionId': data['result']
    }

    return sql_data

def prepare_lfi_data(data):
    lfi_data = {
            'mode': 'write' if 'w' in data['args'][data['config']['argsIndex']+1] else 'read',
            'path': data['args'][data['config']['argsIndex']],
            'realpath': os.path.realpath(data['args'][data['config']['argsIndex']]),
            'poSessionId': data['result']
        }
    return lfi_data