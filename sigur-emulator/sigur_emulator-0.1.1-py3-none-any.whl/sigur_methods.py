from sigure_emulator import responses


def login(command_tag, version, username, password,
          version_must='1.8', username_must='"Administrator"', password_must='""', *args, **kwargs):
    if username != username_must:
        return responses.auth_fail
    elif password != password_must:
        return responses.auth_fail
    elif version != version_must:
        return responses.auth_fail_version
    else:
        return responses.auth_success


def get_ap_info(command_tag, point_number, all_points_states, *args, **kwargs):
    if point_number not in all_points_states:
        return responses.getapinfo_unknown_point
    else:
        return all_points_states[point_number]


def set_ap_mode(command_tag, state, point_number, all_points_states,*args, **kwargs):
    if state not in set_ap_modes:
        return responses.setapinfo_incorrect_state
    else:
        all_points_states[point_number] = responses.point_status_mask.format(point_number, 'ONLINE_'+state)
        return responses.setapinfo_success


def subscribe(*args, **kwargs):
    return responses.subscribe_success


set_ap_modes = ['LOCKED', 'UNLOCKED', 'NORMAL']
methods_dict = {'"LOGIN"': {'method': login, 'type': 'get_point_status'},
                'GETAPINFO': {'method': get_ap_info, 'type': 'get_point_status'},
                'SETAPMODE': {'method': set_ap_mode, 'type': 'set_point_status'},
                '"SUBSCRIBE"': {'method': subscribe, 'type': 'subscribe'}
                }

