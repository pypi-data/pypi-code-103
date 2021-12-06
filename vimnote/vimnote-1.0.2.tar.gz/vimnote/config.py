import configparser
import os

def get_config(path: str):
    # config file doesn't have sections but parser requires sections
    # so just add a default section after loading file
    try:
        f = open(path)
    except IOError:
        content = []
    else:
        with f:
            content = f.readlines()
    content.insert(0, '[DEFAULT]')
    cfg = configparser.ConfigParser()
    cfg.read_string('\n'.join(content))

    # configparser doesn't automatically guess the datatypes based on fallback value
    # so we create a list associating keys, getters, and fallbacks
    # and then use the parser to fill in what it can
    default = cfg['DEFAULT']
    options = [
            ('previewratio', default.getfloat, 0.5),
            ('confirmdelete', default.getboolean, True),
            ('notedir', lambda path, *args, **kwargs: os.path.expanduser(default.get(path, *args, **kwargs)), os.path.expanduser('~/.vimnote/')),
            ('dateformat', default.get, '%I:%M%p %m-%d-%Y'),
            ('defaultsortcol', default.getint, 2),
            ('defaultsortascending', default.getboolean, True) ]
    return { key: getter(key, fallback=fallback) for (key, getter, fallback) in options }
