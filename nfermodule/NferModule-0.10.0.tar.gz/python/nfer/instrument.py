import sys
import types
from inspect import getmembers, isfunction, isbuiltin, stack, getmodule
from functools import wraps
from importlib.machinery import PathFinder, SourceFileLoader
from zipimport import zipimporter
from nfer.nfer import report_interval, Interval, now
from pkgutil import iter_modules
import logging

log = logging.getLogger('nfer')

class watch(object):
    def __init__(self, clsname=None):
        self.clsname = clsname

    def __call__(self, func):
        self.func = func
        if self.clsname is not None:
            self.name = "%s.%s" % (self.clsname, self.func.__name__)
        else:
            self.name = self.func.__name__
        log.debug('Decorating %s' % self.name)

        def wrapped_func(*args, **kwargs):
            begin = now()
            result = self.func(*args, **kwargs)
            # have to create a transient object because update updates in place and doesn't return the modified dict
            passed_args = {'args':",".join(map(str, args))}
            kwargs_strs = dict(map(lambda d: (d[0], str(d[1])), kwargs.items() ))
            passed_args.update(kwargs_strs)
            report_interval(Interval(self.name, begin, now(), passed_args))
            return result
        return wrapped_func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        new_func = self.func.__get__(obj, type)
        return self.__class__(new_func)

symbol_cache = {}
PROBLEM_CLASSES = ["Process", "Thread"]

def instrument_module(module):
    global symbol_cache
    # iterate over the symbol names in the module
    for attr in dir(module):
        # get the symbol associated with the name
        sym = getattr(module, attr)

        # if the symbol is a type (class), instrument its methods
        if type(sym) == type.__class__:
            # skip the list of known problem classes
            if attr in PROBLEM_CLASSES:
                continue

            # iterate over the methods of the class
            for name, meth in getmembers(sym, predicate=isfunction):
                # skip any that we have seen before
                if f"{attr}.{name}" in symbol_cache:
                    continue
                # skip any built-ins, even if overrides - most are read-only anyway
                if isbuiltin(sym):
                    continue
                if name.startswith("__") and name.endswith("__"):
                    continue

                # overwrite the method with the wrapped method
                # print(f"overwrite {attr}.{name}")
                setattr(sym, name, watch(attr)(meth))
                # cache the class so we skip it next time
                symbol_cache[f"{attr}.{name}"] = sym

        # if the symbol is a function, instrument it
        elif callable(sym):
            # skip weird objects without __name__ attributes
            # there are lots of strange things in python modules and some of it is fragile
            if hasattr(sym, "__name__"):
                # skip any that we have seen before
                if attr in symbol_cache:
                    continue

                # overwrite the function in the module with the wrapped function
                # print(f"overwrite {attr}")
                setattr(module, attr, watch()(sym))
                # cache the function so we skip it next time
                symbol_cache[attr] = sym

# class InstrumentFinder:
#     packages=[]
#
#     @classmethod
#     def wrap_exec_module(cls, f):
#         @wraps(f)
#         def exec_module_wrapper(module):
#             ret = f(module)
#             instrument_module(module)
#             return ret
#
#         return exec_module_wrapper
#
#     @classmethod
#     def find_spec (cls, fullname, path=None, target=None):
#         """
#         Check PathFinder to see if it would load the file.
#         If so, wrap its exec_module function with our wrapper which will add instrumentation.
#         This is the least fragile way to do this, as far as I can tell.
#         """
#         path_spec = PathFinder.find_spec(fullname, path, target)
#         #print("Finding spec for fullname: ", fullname)
#         in_package = False
#         for package in InstrumentFinder.packages:
#             in_package = in_package or fullname.startswith(package)
#
#         print("checking %s %r %r" % (fullname, in_package, path_spec is not None))
#         if in_package and path_spec is not None:
#             print("and %r" % type(path_spec.loader))
#
#         if in_package and path_spec is not None:
#             if type(path_spec.loader) == SourceFileLoader or type(path_spec.loader) == zipimporter:
#                 print("instrumenting %s" % fullname)
#                 # unclear which is better - setattr or setting a new types.MethodType
#                 if hasattr(path_spec.loader, "exec_module"):
#                     setattr(path_spec.loader, "exec_module", InstrumentFinder.wrap_exec_module(path_spec.loader.exec_module))
#                     return path_spec
#                 # elif hasattr(path_spec.loader, "load_module"):
#                 #     setattr(path_spec.loader, "load_module", InstrumentFinder.wrap_exec_module(path_spec.loader.load_module))
#
#
#         return None
#
# def instrument_imports(package):
#     if not InstrumentFinder.packages:
#         # This puts our finder right in front of PathFinder
#         # This way we won't disrupt any built-in class loading, hopefully
#         pathfinder_index = sys.meta_path.index(PathFinder)
#         sys.meta_path.insert (pathfinder_index, InstrumentFinder)
#     InstrumentFinder.packages.append(package + ".")

def instrument_package(package):
    # passing a package name
    if isinstance(package, str):
        # check for the package
        if package not in sys.modules:
            # try to import it
            __import__(package)
        # then try getting it
        pkg = sys.modules[package]
    else:
        # otherwise we assume a module was passed
        pkg = package

    for importer, modname, ispkg in iter_modules(pkg.__path__):
        submod_name = "%s.%s" % (pkg.__name__, modname)
        if submod_name in sys.modules and not ispkg:
            instrument_module(sys.modules[submod_name])


def instrument(what=None):
    if what is None:
        stk = stack()
        try:
            instrument_module(sys.modules[getmodule(stk[1][0]).__name__])
        finally:
            # make sure we aren't keeping a reference to stack frames
            del stk
    else:
        # try loading it as a package
        instrument_package(what)