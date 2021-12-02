import attr
from enum import Flag, auto
from miio import Device, DeviceException

class VacuumFeatures(Flag):
    """Flags indicating supported vacuum features."""
    DoNotDisturb = auto()
    FanspeedPercentage = auto()
    FanspeedPresets = auto()
    Mopping = auto()
    SelfEmptying = auto()
    Timers = auto()



@attr.s(auto_attribs=True)
class ModelDescriptor:
    """Container for device model specific meta information."""
    model: str
    name: str
    features: VacuumFeatures

import functools

def needs_feature(feature: VacuumFeatures):
    def wrapper(func):
        @functools.wraps(func)
        def _wrapped(dev: Device, *args, **kwargs):
            if not dev._supports_feature(feature):
                raise DeviceException("%s does not support feature %s" % (dev, feature))

            print("Got called %s %s" % (args, kwargs))
            return func(*args, **kwargs)
        return _wrapped

    return wrapper