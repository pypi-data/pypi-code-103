import logging
from fenics import set_log_level as _backend_set_log_level

logger = logging.getLogger("CRIKit")
"""
The logger for CRIKit. To set the log level, after importing ``crikit`` or any object contained in it, simply use the ``logging`` module like

.. testcode::

     import crikit
     crikit.logging.set_log_level(crikit.logging.WARNING)

"""

DEBUG: int = 10
TRACE: int = 13
PROGRESS: int = 16
INFO: int = 20
WARNING: int = 30
ERROR: int = 40
CRITICAL: int = 50


def set_log_level(level):
    """
        Set the log level for CRIKit and FEniCS. For example,

    .. testcode::

         import crikit
         crikit.logging.set_log_level(crikit.logging.WARNING)

    """
    logger.setLevel(level)
    _backend_set_log_level(level)
