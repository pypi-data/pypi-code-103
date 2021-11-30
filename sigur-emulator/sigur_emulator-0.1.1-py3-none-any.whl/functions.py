from sigure_emulator import sigur_methods
from sigure_emulator import responses
from traceback import format_exc
import datetime


def create_points_dict(points):
    points_dict = {}
    for point in range(points):
        point = point + 1  # Поскольку начинается итерация с 0
        point_state = create_point(point)
        points_dict[str(point)] = point_state
    return points_dict


def create_point(point):
    point_state = responses.point_status_mask.format(point, 'ONLINE_LOCKED')
    return point_state


def get_method(command):
    try:
        return {'status': True, **sigur_methods.methods_dict[command]}
    except KeyError:
        return {'status': False, 'info': format_exc()}


def get_emulated_event_ce_rfid_read(side, rfid_number, wiegand="W42", timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = responses.event_ce_rfid_read_response_mask.format(timestamp, side, wiegand, rfid_number)
    return event


def get_emulated_locked_event(point_num, *args, **kwargs):
    """ Вернуть сэмулированное событие LOCKED для точки доступа point_num"""
    return get_emulated_event_ce_point_changed(point_num, responses.event_ce_mask_elements['lock_state'], *args,
                                               **kwargs)


def get_emulated_unlocked_event(point_num, *args, **kwargs):
    """ Вернуть сэмулированное событие LOCKED для точки доступа point_num"""
    return get_emulated_event_ce_point_changed(point_num, responses.event_ce_mask_elements['unlock_state'], *args,
                                               **kwargs)


def get_emulated_normal_event(point_num, *args, **kwargs):
    """ Вернуть сэмулированное событие LOCKED для точки доступа point_num"""
    return get_emulated_event_ce_point_changed(point_num, responses.event_ce_mask_elements['normal_state'], *args,
                                               **kwargs)


def get_emulated_event_ce_point_changed(point_number, status, timestamp=None):
    """ Вернуть сэмулированное событие status для точки доступа point_number"""
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = responses.event_ce_point_status_response_mask.format(timestamp, status, point_number)
    return event


def add_emulated_event_buffer(point_number, status, *args, **kwargs):
    status = responses.event_ce_mask_elements[status]
    response = get_emulated_event_ce_point_changed(point_number, status)
    return response

