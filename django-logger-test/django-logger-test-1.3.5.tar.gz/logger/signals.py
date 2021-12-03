from django.dispatch import Signal

signal_list = {
    'pizza_done': Signal(providing_args=["task_id", "cose", "category"]),
    'react': Signal(providing_args=["task_id", "version", "name", "category"]),
    'pippo': Signal(providing_args=['pippo_id', "category"]),
    'pluto': Signal(providing_args=['pluto_id', "category"]),
}
