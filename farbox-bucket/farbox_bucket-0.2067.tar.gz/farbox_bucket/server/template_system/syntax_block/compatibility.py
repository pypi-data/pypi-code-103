# coding: utf8

#+font


def syntax_block_compatibility(*args, **kwargs):
    caller = kwargs.pop('caller', None)
    if not caller or not hasattr(caller, '__call__'):
        return ""
    else:
        try:
            return caller()
        except:
            return ""