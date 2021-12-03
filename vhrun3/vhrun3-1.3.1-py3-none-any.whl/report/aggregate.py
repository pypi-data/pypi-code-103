from vhrun3.models import SessionData, StepData
import copy

try:
    import allure

    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False

import platform

from vhrun3 import __version__


def get_platform():
    return {
        "httprunner_version": __version__,
        "python_version": "{} {}".format(
            platform.python_implementation(),
            platform.python_version()
        ),
        "platform": platform.platform()
    }


def aggregate(summary, test_path, error_msg=None):

    step_datas: list = summary.step_datas

    records = []
    records_attachment_list = []
    traceback_msg = ""

    if not step_datas:
        step_datas.append(StepData())

    for item in step_datas:
        teststep = {
            "name": "",
            "data": [
                {
                    "request": {
                        "SSH": "",
                        "executor": "",
                        "params": ""
                    },
                    "response": {
                        "response": "{}"
                    }
                }
            ],
            "stat": {
                "response_time": '0.0'
            },
            "validators": {},
            "extracted_variables": {}
        }

        def expand_steps(step_data, expand_steps_list: list, response_time_list: list):
            if isinstance(step_data.data, SessionData):
                expand_steps_list.append(step_data)
                response_time_list.append(step_data.data.stat.response_time_ms)
            elif isinstance(step_data.data, list):
                for step_item in step_data.data:
                    expand_steps(step_item, expand_steps_list, response_time_list)

        if isinstance(item.data, list):
            expand_steps_list, response_time_list = [], []
            expand_steps(item, expand_steps_list, response_time_list)
            response_time = sum(response_time_list)
            meta_datas_expanded = []
            for sub_step in expand_steps_list:
                tmp_step = copy.deepcopy(teststep)
                if sub_step.data:
                    request_obj = sub_step.data.req_resps[0].request
                    response_obj = sub_step.data.req_resps[0].response
                    if hasattr(request_obj, "method"):
                        tmp_step["data"][0]["request"] = {
                            "method": request_obj.method,
                            "headers": request_obj.headers,
                            "url": request_obj.url,
                            "body": request_obj.body,
                            "cookies": request_obj.cookies,
                        }
                        tmp_step["data"][0]["response"] = {
                            "status_code": response_obj.status_code,
                            "headers": response_obj.headers,
                            "body": response_obj.body,
                            "cookies": response_obj.cookies,
                        }

                    else:
                        tmp_step["data"][0]["request"] = request_obj.body
                        tmp_step["data"][0]["response"]["response"] = response_obj.body["body"]
                if sub_step.data:
                    tmp_step["validators"] = sub_step.data.validators
                tmp_step["name"] = sub_step.name
                tmp_step["stat"]["response_time"] = str(round(sub_step.data.stat.response_time_ms, 2))
                name = sub_step.name
                meta_datas_expanded.append(tmp_step)
        else:
            meta_datas_expanded = []
            tmp_step = copy.deepcopy(teststep)
            if item.data:
                request_obj = item.data.req_resps[0].request
                response_obj = item.data.req_resps[0].response
                if hasattr(request_obj, "method"):
                    tmp_step["data"][0]["request"] = {
                        "method": request_obj.method,
                        "headers": request_obj.headers,
                        "url": request_obj.url,
                        "body": request_obj.body,
                        "cookies": request_obj.cookies,
                    }
                    tmp_step["data"][0]["response"] = {
                        "status_code": response_obj.status_code,
                        "headers": response_obj.headers,
                        "body": response_obj.body,
                        "cookies": response_obj.cookies,
                    }
                else:
                    tmp_step["data"][0]["request"] = request_obj.body
                    tmp_step["data"][0]["response"]["response"] = response_obj.body["body"]
            if item.data:
                tmp_step["validators"] = item.data.validators
                response_time = item.data.stat.response_time_ms
            else:
                response_time = 0
            tmp_step["name"] = item.name
            name = item.name
            meta_datas_expanded.append(tmp_step)

        def expand_attachment(step_data: StepData, expand_attachment_list: list):
            if isinstance(step_data.data, SessionData):
                records_attachment_list.append(step_data.data.attachment)
                if step_data.data.attachment:
                    expand_attachment_list.append(step_data.data.attachment)
            elif isinstance(step_data.data, list):
                for step_item in step_data.data:
                    expand_attachment(step_item, expand_attachment_list)

        expand_attachment_list = copy.deepcopy([])
        expand_attachment(item, expand_attachment_list)

        if expand_attachment_list and "None" not in error_msg:
            expand_attachment_list.append(error_msg)
            traceback_msg += "\n" + name + ": \n".join(expand_attachment_list)
        if expand_attachment_list:
            traceback_msg += "\n" + name + ": \n".join(expand_attachment_list)
        if not expand_attachment_list and "None" not in error_msg:
            traceback_msg = error_msg

        step = {
            "attachment": traceback_msg,
            "name": name,
            "status": "success",
            "meta_datas_expanded": meta_datas_expanded,
            "response_time": str(round(response_time, 2))
        }
        if step["attachment"]:
            step["status"] = "failure"
            summary.success = False
        records.append(step)

    succss_list = [item for item in records_attachment_list if not item]
    fail_list = [item for item in records_attachment_list if item]
    if summary.success is True:
        success_num, fail_num = 1, 0
    else:
        success_num, fail_num = 0, 1

    case = {test_path: {
        "success": summary.success,
        "stat": {
            "testcases": {
                "total": 1,
                "success": success_num,
                "fail": fail_num
            },
            "teststeps": {
                "total": len(records_attachment_list),
                "failures": len(fail_list),
                "errors": 0,
                "skipped": 0,
                "expectedFailures": 0,
                "unexpectedSuccesses": 0,
                "successes": len(succss_list)
            }
        },
        "time": {
            "start_at": summary.time.start_at,
            "duration": summary.time.duration
        },
        "details": [
            {
                "success": summary.success,
                "stat": {

                    "total": len(records_attachment_list),
                    "failures": len(fail_list),
                    "errors": 0,
                    "skipped": 0,
                    "expectedFailures": 0,
                    "unexpectedSuccesses": 0,
                    "successes": len(succss_list)

                },
                "time": {
                    "start_at": summary.time.start_at,
                    "duration": summary.time.duration
                },
                "records": records,
                "name": summary.name,
                "in_out": {
                    "in": {
                        "aaa": 123
                    },
                    "out": {}
                }
            }
        ]
    }}

    from vhrun3.report.stringify import stringify_summary
    stringify_summary(case.get(test_path))
    aggregated_summary = {
        "success": summary.success,
        "stat": {
            "testcases": {
                "total": 1,
                "success": success_num,
                "fail": fail_num
            },
            "teststeps": {
                "total": len(step_datas),
                "failures": len(fail_list),
                "errors": 0,
                "skipped": 0,
                "expectedFailures": 0,
                "unexpectedSuccesses": 0,
                "successes": len(succss_list)
            }
        },
        "time": {
            "start_at": summary.time.start_at,
            "duration": summary.time.duration
        },
        "platform": get_platform(),
        "suites": {}
    }
    aggregated_summary["suites"].update(case)

    return aggregated_summary, traceback_msg


def summary_gather(summry_list):
    goal_summary = {
        "success": True,
        "stat": {
            "testcases": {
                "total": 0,
                "success": 0,
                "fail": 0
            },
            "teststeps": {
                "total": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "expectedFailures": 0,
                "unexpectedSuccesses": 0,
                "successes": 0
            }
        },
        "time": {
            "start_at": 0,
            "duration": 0
        },
        "platform": {
            "httprunner_version": "3.1.6",
            "python_version": "CPython 3.7.3",
            "platform": "Linux-3.10.0-693.el7.x86_64-x86_64-with-centos-7.8.2003-Core"
        },
        "suites": {}
    }

    suite_key_list = []
    for index, item in enumerate(summry_list):
        for value in ["total", "success", "fail"]:
            goal_summary["stat"]["testcases"][value] += item["stat"]["testcases"][value]

        for value in ["total", "failures", "errors", "skipped", "expectedFailures", "unexpectedSuccesses", "successes"]:
            goal_summary["stat"]["teststeps"][value] += item["stat"]["teststeps"][value]

        goal_summary["time"]["duration"] += float(item["time"]["duration"])

        suite_key_list += list(item["suites"].keys())

    py_path_list: list = list(set(suite_key_list))

    case_dict = {list(item["suites"].keys())[0]: [] for item in summry_list if list(item["suites"].keys())[0] in py_path_list}

    for item in summry_list:
        key_name = list(item["suites"].keys())[0]
        if key_name in case_dict.keys():
            case_dict[key_name].append(item["suites"][key_name])

    case_summary = {
        "stat": {
            "testcases": {
                "total": 0,
                "success": 0,
                "fail": 0
        },
            "teststeps": {
                "total": 0,
                "failures": 0,
                "errors": 0,
                "skipped": 0,
                "expectedFailures": 0,
                "unexpectedSuccesses": 0,
                "successes": 0
        }
    },
        "time": {
            "start_at": 0,
            "duration": 0
    },
        "details": []
    }

    list_obj = []
    for suite_key, test_cases in case_dict.items():
        case_summary_dict = copy.deepcopy(case_summary)
        flag_list = copy.deepcopy(list_obj)
        for case in test_cases:
            for value in ["total", "success", "fail"]:
                case_summary_dict["stat"]["testcases"][value] += case["stat"]["testcases"][value]
            for value in ["total", "failures", "errors", "skipped", "expectedFailures", "unexpectedSuccesses",
                          "successes"]:
                case_summary_dict["stat"]["teststeps"][value] += case["stat"]["teststeps"][value]
            case_summary_dict["time"]["duration"] += float(case["time"]["duration"])

            flag_list.append(case["success"])
            case_summary_dict["details"] += case["details"]
        goal_summary["suites"].update({suite_key: case_summary_dict})
        goal_summary["suites"][suite_key]["success"] = all(flag_list)

    return goal_summary
