import abc
import asyncio
import functools


def wrap_async_to_sync(f):
    @functools.wraps(f)
    def wrap(instance, *args, **kwargs):
        return asyncio.run(f(instance, *args, **kwargs))

    return wrap


class AsyncToSyncProxy:
    def __init__(self, instance):
        self.__instance = instance

    def __getattr__(self, item):
        try:
            result = getattr(self.__instance, item)
        except AttributeError:
            result = getattr(self.__instance.__class__, item)
        return result

    def __setattr__(self, key, value):
        if not key == "_AsyncToSyncProxy__instance":
            return setattr(self.__instance, key, value)
        return super().__setattr__(key, value)

    def __repr__(self):
        return f"AsyncToSyncProxy{self.__instance}"


class AsyncToSyncProxyMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, namespace):
        sync_namespace = namespace.copy()

        for key, value in sync_namespace.copy().items():
            if key == "__init__":
                sync_namespace[key] = AsyncToSyncProxy.__init__
            if asyncio.iscoroutinefunction(value):
                sync_namespace[key] = wrap_async_to_sync(value)

        namespace["sync"] = property(
            type(f"AsyncToSyncProxy{name}", tuple([AsyncToSyncProxy]), sync_namespace)
        )
        return super().__new__(mcs, name, bases, namespace)
