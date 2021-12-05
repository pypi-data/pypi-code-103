import platform as pfm


def is_windows():
    return pfm.system().lower().find('windows') > -1
