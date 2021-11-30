# -*- coding: utf-8 -*-

from fast_tracker.common.object_wrapper import wrap_function_wrapper


def _nr_wrapper_Motor_getattr_(wrapped, instance, args, kwargs):
    def _bind_params(name, *args, **kwargs):
        return name

    name = _bind_params(*args, **kwargs)

    if name.startswith('__') or name.startswith('_nr_'):
        raise AttributeError('%s class has no attribute %s. To access '
                             'use object[%r].' % (instance.__class__.__name__,
                                                  name, name))

    return wrapped(*args, **kwargs)


def patch_motor(module):
    if (hasattr(module, 'version_tuple') and
            module.version_tuple >= (0, 6)):
        return

    patched_classes = ['MotorClient', 'MotorReplicaSetClient', 'MotorDatabase',
                       'MotorCollection']
    for patched_class in patched_classes:
        if hasattr(module, patched_class):
            wrap_function_wrapper(module, patched_class + '.__getattr__',
                                  _nr_wrapper_Motor_getattr_)
