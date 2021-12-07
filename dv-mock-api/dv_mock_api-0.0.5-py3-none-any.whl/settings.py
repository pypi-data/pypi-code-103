from http import HTTPStatus
from dv_mock_api.enums import ObjectProperty, ObjectType, ResponseTypes

REPORT_DIRECTORY = "reports"

MAPPING = {
    ObjectType.PARTNERS: {
        "1": {
            ResponseTypes.GET: HTTPStatus.OK,
            ResponseTypes.PATCH: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectType.ADVERTISERS: {
                "1": {
                    ResponseTypes.GET: HTTPStatus.OK,
                    ResponseTypes.PATCH: HTTPStatus.OK,
                    ObjectProperty.TIMEOUT: 1,
                    ObjectType.LINEITEMS: {
                        "1": {
                            ResponseTypes.GET: HTTPStatus.OK,
                            ResponseTypes.PATCH: HTTPStatus.OK,
                            ObjectProperty.TIMEOUT: 1,
                        },
                        "2": {
                            ResponseTypes.GET: HTTPStatus.OK,
                            ResponseTypes.PATCH: HTTPStatus.REQUEST_TIMEOUT,
                            ObjectProperty.TIMEOUT: 1,
                        },
                        "3": {
                            ResponseTypes.GET: HTTPStatus.OK,
                            ResponseTypes.PATCH: HTTPStatus.REQUEST_TIMEOUT,
                            ObjectProperty.TIMEOUT: 1,
                        }
                    }
                }
            }
        },
        "4": {
            ResponseTypes.GET: HTTPStatus.OK,
            ResponseTypes.PATCH: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectType.ADVERTISERS: {
                "5": {
                    ResponseTypes.GET: HTTPStatus.OK,
                    ResponseTypes.PATCH: HTTPStatus.OK,
                    ObjectProperty.TIMEOUT: 1,
                    ObjectType.LINEITEMS: {
                        "6": {
                            ResponseTypes.GET: HTTPStatus.TOO_MANY_REQUESTS,
                            ResponseTypes.PATCH: HTTPStatus.OK,
                            ObjectProperty.TIMEOUT: 3,
                        },
                        "7": {
                            ResponseTypes.GET: HTTPStatus.REQUEST_TIMEOUT,
                            ResponseTypes.PATCH: HTTPStatus.OK,
                            ObjectProperty.TIMEOUT: 10,
                        },
                        "8": {
                            ResponseTypes.GET: HTTPStatus.INTERNAL_SERVER_ERROR,
                            ResponseTypes.PATCH: HTTPStatus.OK,
                            ObjectProperty.TIMEOUT: 5,
                        }
                    }
                },
                "9": {
                    ResponseTypes.GET: HTTPStatus.REQUEST_TIMEOUT,
                    ResponseTypes.PATCH: HTTPStatus.OK,
                    ObjectProperty.TIMEOUT: 1,
                    ObjectType.LINEITEMS: {}
                }
            }
        },
        "13": {
            ResponseTypes.GET: HTTPStatus.UNAUTHORIZED,
            ResponseTypes.PATCH: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectType.ADVERTISERS: {}
        },
    },
    ObjectType.REPORTS: {
        "1": {
            "name": "spend report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "spend.csv"
        },
        "2": {
            "name": "billable outcome report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "billable_outcome.csv"
        },
        "3": {
            "name": "platform fee report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "platform_fee.csv"
        },
        "4": {
            "name": "broken report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.REQUEST_TIMEOUT,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "empty.csv"
        },
        "5": {
            "name": "cant create report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.INTERNAL_SERVER_ERROR,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "empty.csv"
        },
        "6": {
            "name": "cant run report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.INTERNAL_SERVER_ERROR,
            ResponseTypes.GET_REPORT: HTTPStatus.OK,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "empty.csv"
        },
        "7": {
            "name": "cant get report",
            ResponseTypes.CREATE_REPORT: HTTPStatus.OK,
            ResponseTypes.RUN_REPORT: HTTPStatus.OK,
            ResponseTypes.GET_REPORT: HTTPStatus.UNAUTHORIZED,
            ResponseTypes.DOWNLOAD_FILE: HTTPStatus.OK,
            ObjectProperty.TIMEOUT: 1,
            ObjectProperty.FILE: "empty.csv"
        }
    }
}
