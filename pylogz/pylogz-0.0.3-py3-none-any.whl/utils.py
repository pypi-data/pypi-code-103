import os

_logger_split_newlines: bool = bool(os.getenv('PYLOGZ_SPLIT_NEWLINES', 'false').lower() in {'true', 'yes', '1'})

def convert_log(*msgs, split_newline: bool = _logger_split_newlines):
    _msgs = []
    for msg in msgs:
        if isinstance(msg, list):
            for m in msg: _msgs.append(f'- {m}')
        elif isinstance(msg, dict):
            for k,v in msg.items():
                _msgs.append(f'- {k}: {v}')
        elif isinstance(msg, str):
            if split_newline:  _msgs.extend(msg.split('\n'))
            else: _msgs.append(msg)
        else: _msgs.append(f'{msg}')
    return [i for i in _msgs if i]

