"""
Tasks for interacting with Zoho CRM.
"""
try:
    from zohocrm_prefect_tasks.tasks.records import Create, List, ListDeleted, Search, Fetch, Update, Upsert, Delete
    from zohocrm_prefect_tasks.client import ApiClient
    from zohocrm_prefect_tasks.utils import *
except ImportError:
    raise ImportError(
        'Using `prefect.tasks.zohocrm` requires Prefect to be installed with the "zcrmsdk" '
        'extra. '
    )

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions
