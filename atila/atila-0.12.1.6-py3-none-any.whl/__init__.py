"""
2015. 12. 10
Hans Roh
"""

__version__ = "0.12.1.6"

version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))
assert len ([x for  x in version_info [:2] if isinstance (x, int)]) == 2, 'major and minor version should be integer'

from .patches import skitaipatch
from .Atila import Atila
import os
from .events import *
from .collectors.multipart_collector import FileWrapper

file = FileWrapper
def preference (*args, **kargs):
    import skitai
    return skitai.preference (*args, **kargs)


def load (target, pref = None):
    from rs4 import importer
    from rs4.attrdict import AttrDict
    import os, copy

    def init_app (directory, pref):
        modinit = os.path.join (directory, "__init__.py")
        if os.path.isfile (modinit):
            mod = importer.from_file ("temp", modinit)
            initer = None
            if hasattr (mod, "__config__"):
                initer = mod.__config__
            elif hasattr (mod, "__setup__"):
                initer = mod.__setup__
            elif hasattr (mod, "bootstrap"): # old version
                initer = mod.bootstrap (pref)
            initer and initer (pref)

    if hasattr (target, "__file__"):
        if hasattr (target, '__skitai__'):
            target = target.__skitai__

        if hasattr (target, '__app__'):
            module, abspath, directory = target, os.path.abspath (target.__file__), None

        else:
            directory = os.path.abspath (os.path.join (os.path.dirname (target.__file__), "export", "skitai"))
            if os.path.isfile (os.path.join (directory, 'wsgi.py')):
                _script = 'wsgi'
            else:
                _script = '__export__' # old version
            module, abspath = importer.importer (directory, _script)

    else:
        directory, script = os.path.split (target)
        module, abspath = importer.importer (directory, script [-3:] == ".py" and script [:-3] or script)

    pref = pref or skitai.preference ()
    if directory:
        init_app (directory, pref)
        app = module.app
    else:
        module.__config__ (pref)
        app = module.__app__ ()

    for k, v in copy.copy (pref).items ():
        if k == "config":
            if not hasattr (app, 'config'):
                app.config = v
            else:
                for k, v in copy.copy (pref.config).items ():
                    app.config [k] = v
        else:
            setattr (app, k, v)

    wss = AttrDict ()
    hasattr (module, '__setup__') and module.__setup__ (app, {})
    hasattr (module, '__mount__') and module.__mount__ (app, {})
    hasattr (module, '__umount__') and app.before_umount (module.__umount__)
    return app
