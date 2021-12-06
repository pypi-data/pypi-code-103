def read_bool_setting(settings, setting_name, default=False):
    try:
        s = settings.value(setting_name)
        if s is not None:
            s_int = int(s)
            return False if s_int == 0 else True
        else:
            return default
    except ValueError:
        return default


def read_int_setting(settings, setting_name, default=0):
    try:
        s = settings.value(setting_name)
        if s is not None:
            return int(s)
        else:
            return default
    except ValueError:
        return default


def write_bool_setting(settings, setting_name, value):
    settings.setValue(setting_name, 1 if value else 0)
