#!/usr/bin/env python
# -*- coding: utf-8 -*--

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/


import warnings


def deprecated(deprecated_in, removed_in=None, details=None):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Parameters
    ----------
    deprecated_in: `str`
        Version of ADS where this function deprecated.
    removed_in: `str`
        Future version where this function will be removed.
    details: `str`
        More information to be shown.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Method {func.__name__} is "
                f"deprecated in {deprecated_in} and will be "
                f"removed in {removed_in if removed_in else 'a future release'}."
                f"{'' if not details else ' ' + details}",
                DeprecationWarning,
                stacklevel=2,
            )
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
