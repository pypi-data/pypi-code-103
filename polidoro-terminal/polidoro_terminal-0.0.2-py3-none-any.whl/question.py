def question(text, default=None, resp_type=None):
    if default is None:
        default_str = ''
    else:
        default_str = f'({default})'
    resp = input(f'{text}{default_str}: ')
    if not resp:
        return default

    if resp_type:
        return resp_type(resp)
    return resp
