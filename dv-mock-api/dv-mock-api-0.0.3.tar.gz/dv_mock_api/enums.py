from enum import Enum


class ObjectType(Enum):
    PARTNERS = "partners"
    ADVERTISERS = "advertisers"
    LINEITEMS = "lineitems"
    REPORTS = "reports"


class ObjectProperty(Enum):
    TIMEOUT = "timeout"
    FILE = "file"


class ResponseTypes(Enum):
    GET = "get_response"
    PATCH = "patch_response"
    CREATE_REPORT = "create_report_response"
    RUN_REPORT = "run_report_response"
    GET_REPORT = "get_report_response"
    DOWNLOAD_FILE = "download_file_response"
