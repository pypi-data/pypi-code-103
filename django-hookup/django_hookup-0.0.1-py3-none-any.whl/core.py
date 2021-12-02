from operator import itemgetter
from importlib import import_module

from django.apps import apps
from django.utils.module_loading import module_has_submodule

_django_hookup = {}
_searched_for_django_hookup = False


def get_app_modules():
    """
    Generator function that yields a module object for each installed app
    yields tuples of (app_name, module)
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(submodule_name):
    """
    Searches each app module for the specified submodule
    yields tuples of (app_name, module)
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, submodule_name):
            yield name, import_module("%s.%s" % (name, submodule_name))


def register(hook_name, fn=None, order=0):
    """
    Register hook for ``hook_name``. Can be used as a decorator::

        @register('hook_name')
        def my_hook(...):
            pass

    or as a function call::

        def my_hook(...):
            pass
        register('hook_name', my_hook)
    """

    # Pretend to be a decorator if fn is not supplied
    if fn is None:

        def decorator(fn):
            register(hook_name, fn, order=order)
            return fn

        return decorator

    if hook_name not in _django_hookup:
        _django_hookup[hook_name] = []
    _django_hookup[hook_name].append((fn, order))


def search_for_django_hookup():
    global _searched_for_django_hookup
    if not _searched_for_django_hookup:
        list(get_app_submodules("hooks"))
        _searched_for_django_hookup = True


def get_hooks(hook_name):
    """Return the hooks function sorted by their order."""
    search_for_django_hookup()
    hooks = _django_hookup.get(hook_name, [])
    hooks = sorted(hooks, key=itemgetter(1))
    return [hook[0] for hook in hooks]
