# -*- coding: utf-8 -*-
import imp
import logging
import sys

_logger = logging.getLogger(__name__)

try:
    from importlib import find_loader
except ImportError:
    find_loader = None

_import_hooks = {}

_ok_modules = (
        'urllib', 'urllib2', 'httplib', 'http.client', 'urllib.request', 'fast_tracker.agent', 'gunicorn.app.base',
        'wsgiref.simple_server', 'gevent.wsgi', 'gevent.pywsgi', 'cheroot.wsgi', 'cherrypy.wsgiserver',
        'flup.server.cgi', 'flup.server.ajp_base', 'flup.server.fcgi_base', 'flup.server.scgi_base',
        'meinheld.server', 'paste.httpserver', 'waitress.server', 'gevent.monkey', 'asyncio.base_events'
)

_uninstrumented_modules = set()


def register_import_hook(name, callable):
    imp.acquire_lock()

    try:
        hooks = _import_hooks.get(name, None)

        if name not in _import_hooks or hooks is None:
            module = sys.modules.get(name, None)

            if module is not None:
                if module.__name__ not in _ok_modules:
                    _logger.debug('模块 %s 在调用fast_tracker.agent.initialize之前已经导入.' % module)

                    _uninstrumented_modules.add(module.__name__)

                _import_hooks[name] = None

                callable(module)

            else:
                _import_hooks[name] = [callable]

        else:

            _import_hooks[name].append(callable)

    finally:
        imp.release_lock()


def _notify_import_hooks(name, module):

    hooks = _import_hooks.get(name, None)

    if hooks is not None:
        _import_hooks[name] = None

        for callable in hooks:
            callable(module)


class _ImportHookLoader:

    def load_module(self, fullname):

        module = sys.modules[fullname]
        _notify_import_hooks(fullname, module)

        return module


class _ImportHookChainedLoader:

    def __init__(self, loader):
        self.loader = loader

    def load_module(self, fullname):
        module = self.loader.load_module(fullname)

        _notify_import_hooks(fullname, module)

        return module


class ImportHookFinder:

    def __init__(self):
        self._skip = {}

    def find_module(self, fullname, path=None):
        if fullname not in _import_hooks:
            return None
        if fullname in self._skip:
            return None

        self._skip[fullname] = True

        try:

            if find_loader:
                loader = find_loader(fullname, path)

                if loader:
                    return _ImportHookChainedLoader(loader)

            else:
                __import__(fullname)
                return _ImportHookLoader()

        finally:
            del self._skip[fullname]


def import_hook(name):
    def decorator(wrapped):
        register_import_hook(name, wrapped)
        return wrapped
    return decorator


def import_module(name):
    __import__(name)   # 动态导入模块，并返回模块包路径
    # sys.modules是一个全局字典，该字典是python启动后就加载在内存中。每当程导入新的模块， sys.modules都将记录这些模块。
    # 字典sys.modules对于加载模块起到了缓冲的作用，这样可以知道项目中用了哪些模块。
    return sys.modules[name]
