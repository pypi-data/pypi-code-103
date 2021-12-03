import json
import os
import time
import uuid
from datetime import datetime
from typing import List, Dict, Text, NoReturn
from vhrun3.builtin.functions import get_process_thread_id
import pytest
from vhrun3.parser import function_regex_compile, parse_function_params
from vhrun3.utils import print_info
from vhrun3.models import SSHRequestData, SSHResponseData
from vhrun3.models import SessionData, SSHReqRespData
import copy
import traceback

try:
    import allure
    from vhrun3.report.allure_report.allure_step import teststep_allure_step

    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False

from loguru import logger
from vhrun3.report.aggregate import aggregate
from vhrun3 import utils, exceptions
from vhrun3.client import HttpSession
from vhrun3.exceptions import ValidationFailure, ParamsError
from vhrun3.ext.uploader import prepare_upload_step
from vhrun3.loader import load_project_meta, load_testcase_file
from vhrun3.parser import build_url, parse_data, parse_variables_mapping
from vhrun3.response import ResponseObject, SSHResponseObject
from vhrun3.testcase import Config, Step
from vhrun3.utils import merge_variables
from vhrun3.models import (
    TConfig,
    TStep,
    VariablesMapping,
    StepData,
    TestCaseSummary,
    TestCaseTime,
    TestCaseInOut,
    ProjectMeta,
    TestCase,
    Hooks,
)
from vhrun3.client import SSH
from vhrun3.cli import case_summary_list


class HttpRunner(object):
    config: Config
    teststeps: List[Step]

    success: bool = False  # indicate testcase execution result
    __config: TConfig
    __teststeps: List[TStep]
    __project_meta: ProjectMeta = None
    __case_id: Text = ""
    __export: List[Text] = []
    __step_datas: List[StepData] = []
    __session: HttpSession = None
    __ssh: SSH = SSH()
    __session_variables: VariablesMapping = {}
    # time
    __start_at: float = 0
    __duration: float = 0
    # log
    __log_path: Text = ""

    def __init_tests__(self) -> NoReturn:
        self.__config = self.config.perform()
        self.__teststeps = []
        for step in self.teststeps:
            self.__teststeps.append(step.perform())

    @property
    def raw_testcase(self) -> TestCase:
        if not hasattr(self, "__config"):
            self.__init_tests__()

        return TestCase(config=self.__config, teststeps=self.__teststeps)

    def with_project_meta(self, project_meta: ProjectMeta) -> "HttpRunner":
        self.__project_meta = project_meta
        return self

    def with_session(self, session: HttpSession) -> "HttpRunner":
        self.__session = session
        return self

    def with_case_id(self, case_id: Text) -> "HttpRunner":
        self.__case_id = case_id
        return self

    def with_variables(self, variables: VariablesMapping) -> "HttpRunner":
        self.__session_variables = variables
        return self

    def with_export(self, export: List[Text]) -> "HttpRunner":
        self.__export = export
        return self

    def __call_skip_if(
            self, skip_if_list: Hooks, step_variables: VariablesMapping, skip_if_msg: Text,
    ) -> dict:
        """ call skipIf actions.

        Args:  ${func()}

        step_variables: current step variables to call hook, include two special variables

                request: parsed request dict
                response: ResponseObject for current response

            hook_msg: setup/teardown request/testcase

        """
        logger.info(f"call skip_if actions: {skip_if_msg}")

        if not isinstance(skip_if_list, List):
            logger.error(f"Invalid skip format: {skip_if_list}")
            raise

        result_dict = {}
        for skip_if in skip_if_list:
            if isinstance(skip_if, Text):
                # "${func()}"
                logger.debug(f" call skip_if function: {skip_if}")
                ret = parse_data(skip_if, step_variables, self.__project_meta.functions)
                result_dict.update({skip_if: ret})
            else:
                logger.error(f"Invalid skip_if format: {skip_if}")

        return result_dict

    def __call_hooks(
            self, hooks: Hooks, step_variables: VariablesMapping, hook_msg: Text,
    ) -> NoReturn:
        """ call hook actions.

        Args:
            hooks (list): each hook in hooks list maybe in two format.

                format1 (str): only call hook functions.
                    ${func()}
                format2 (dict): assignment, the value returned by hook function will be assigned to variable.
                    {"var": "${func()}"}

            step_variables: current step variables to call hook, include two special variables

                request: parsed request dict
                response: ResponseObject for current response

            hook_msg: setup/teardown request/testcase

        """
        def get_parsed_function(hook_function, hook_eval):
            try:
                func_match = function_regex_compile.match(hook_function, 0)
                func_name = func_match.group(1)
                func_params_str = func_match.group(2)
                function_meta = parse_function_params(func_params_str)
                args = function_meta["args"]
                kwargs = function_meta["kwargs"]
                parsed_args = parse_data(args, step_variables, self.__project_meta.functions)
                parsed_kwargs = parse_data(kwargs, step_variables, self.__project_meta.functions)
                return {hook_function: {"func_name": func_name,
                                        "args": parsed_args,
                                        "kwargs": parsed_kwargs,
                                        "eval_ret": hook_eval}}
            except Exception:
                logger.error(f"Invalid hook format: {hook_function}")

        logger.info(f"call hook actions: {hook_msg}")

        if not isinstance(hooks, List):
            logger.error(f"Invalid hooks format: {hooks}")
            return

        hook_variables = {}
        parsed_hooks = []
        for hook in hooks:
            if isinstance(hook, Text):
                # format 1: "${func()}"
                logger.debug(f"call hook function: {hook}")
                hook_content_eval = parse_data(hook, step_variables, self.__project_meta.functions)
                parsed_hooks.append(get_parsed_function(hook, hook_content_eval))
            elif isinstance(hook, Dict) and len(hook) == 1:
                # format 2: {"var": "${func()}"}
                var_name, hook_content = list(hook.items())[0]
                hook_content_eval = parse_data(
                    hook_content, step_variables, self.__project_meta.functions
                )
                logger.debug(
                    f"call hook function: {hook_content}, got value: {hook_content_eval}"
                )
                logger.debug(f"assign variable: {var_name} = {hook_content_eval}")
                step_variables[var_name] = hook_content_eval
                hook_variables[var_name] = hook_content_eval
                parsed_hooks.append(get_parsed_function(hook_content, hook_content_eval))
            else:
                logger.error(f"Invalid hook format: {hook}")

        return hook_variables, parsed_hooks

    def __run_step_request(self, step: TStep, protocol=None) -> StepData:
        """run teststep: request"""
        step_data = StepData(name=step.name)

        setup_hook_list = []
        teardown_hook_list = []

        try:
            if protocol is None:
                # parse
                prepare_upload_step(step, self.__project_meta.functions)
                request_dict = step.request.dict()
                request_dict.pop("upload", None)
                parsed_request_dict = parse_data(
                    request_dict, step.variables, self.__project_meta.functions
                )
                parsed_request_dict["headers"].setdefault(
                    "HRUN-Request-ID",
                    f"HRUN-{self.__case_id}-{str(int(time.time() * 1000))[-6:]}",
                )
                step.variables["request"] = parsed_request_dict
                # setup hooks
                try:
                    if step.setup_hooks:
                        setup_variables, parsed_hooks = self.__call_hooks(step.setup_hooks, step.variables, "setup request")
                        step_data.export_vars.update(setup_variables)
                        setup_hook_list = parsed_hooks
                except Exception as e:
                    error_msg = str(traceback.format_exc())
                    self.__session.data.err_list.append(error_msg)
                    self.__ssh.data.err_list.append(error_msg)
                # prepare arguments
                method = parsed_request_dict.pop("method")
                url_path = parsed_request_dict.pop("url")
                url = build_url(self.__config.base_url, url_path)
                parsed_request_dict["verify"] = self.__config.verify
                parsed_request_dict["json"] = parsed_request_dict.pop("req_json", {})

                # request
                resp = self.__session.request(method, url, **parsed_request_dict)
                resp_obj = ResponseObject(resp)
                parsed_request_dict.update({"url": url, "method": method})
                request_data = parsed_request_dict
                try:
                    body = json.loads(resp.text)
                except Exception:
                    body = resp.text
                response_data = {"status_code": resp.status_code,
                                 "headers": resp.headers,
                                 "body": body}
                step.variables["response"] = response_data
            else:

                raw_connection = step.connection
                parsed_connection = parse_data(
                    raw_connection, step.variables, self.__project_meta.functions
                )

                try:
                    # ssh connection
                    ssh_ip = parsed_connection.get('ssh_ip', None)
                    ssh_port = parsed_connection.get('ssh_port', 22)
                    ssh_user = parsed_connection.get('ssh_user')
                    ssh_password = parsed_connection.get('ssh_password')
                    connection = {"hostname": ssh_ip, "port": ssh_port, "username": ssh_user, "password": ssh_password}
                    # ssh fields
                    ssh_type = step.ssh_type
                    if ssh_type == "shell":
                        cmd_list = step.ssh_cmd
                        parsed_cmd_list = parse_data(
                            cmd_list, step.variables, self.__project_meta.functions
                        )
                        parsed_request_dict = {"executor": parsed_cmd_list[0], "params": parsed_cmd_list[1]}
                    elif ssh_type == "upload" or ssh_type == "download":
                        parsed_path_list = parse_data(
                            step.paths, step.variables, self.__project_meta.functions
                        )
                        local_path, remote_path = parsed_path_list
                        parsed_request_dict = {"local_path": os.path.join(self.__project_meta.RootDir, local_path),
                                               "remote_path": remote_path}
                    else:
                        raise exceptions.ParamsError("SSH relative params missed!")
                except Exception as e:
                    raise e
                step.variables["request"] = parsed_request_dict
                # setup hooks
                try:
                    if step.setup_hooks:
                        setup_variables, parsed_hooks = self.__call_hooks(step.setup_hooks, step.variables, "setup request")
                        step_data.export_vars.update(setup_variables)
                        setup_hook_list = parsed_hooks
                except Exception as e:
                    error_msg = str(traceback.format_exc())
                    self.__session.data.err_list.append(error_msg)
                    self.__ssh.data.err_list.append(error_msg)

                # request
                resp = self.__ssh.request(
                    connection,
                    ssh_type,
                    parsed_request_dict,
                    name=step.name
                )
                resp_obj = SSHResponseObject(resp)
                print_info(resp_obj.resp_obj)

                parsed_request_dict["SSH"] = parsed_connection
                request_data = SSHRequestData(
                    body=parsed_request_dict,
                )
                response_data = SSHResponseData(
                    body=resp_obj.resp_obj,
                )
                req_resp_data = SSHReqRespData(request=request_data, response=response_data)

                self.__ssh.data.req_resps = [req_resp_data]

                request_data, response_data = resp.get("request"), resp.get("body")
                step.variables["response"] = response_data

            # extract
            extractors = step.extract
            extract_mapping = resp_obj.extract(extractors)
            step_data.export_vars.update(extract_mapping)
            step.variables.update(extract_mapping)

            # teardown hooks
            try:
                if step.teardown_hooks:
                    teardown_variables, parsed_hooks = self.__call_hooks(step.teardown_hooks, step.variables, "teardown request")
                    step_data.export_vars.update(teardown_variables)
                    teardown_hook_list = parsed_hooks
            except Exception:
                error_msg = str(traceback.format_exc())
                self.__session.data.err_list.append(error_msg)
                self.__ssh.data.err_list.append(error_msg)

            # validate
            validators = step.validators
            session_success = False

            def log_req_resp_details():
                if protocol is None:
                    err_msg = "\n{} DETAILED REQUEST & RESPONSE {}\n".format("*" * 32, "*" * 32)

                    # log request
                    err_msg += "====== request details ======\n"
                    err_msg += f"url: {url}\n"
                    err_msg += f"method: {method}\n"
                    headers = parsed_request_dict.pop("headers", {})
                    err_msg += f"headers: {headers}\n"
                    for k, v in parsed_request_dict.items():
                        v = utils.omit_long_data(v)
                        err_msg += f"{k}: {repr(v)}\n"

                    err_msg += "\n"

                    # log response
                    err_msg += "====== response details ======\n"
                    err_msg += f"status_code: {resp.status_code}\n"
                    err_msg += f"headers: {resp.headers}\n"
                    err_msg += f"body: {repr(resp.text)}\n"
                    logger.error(err_msg)
                else:
                    err_msg = "\n{} DETAILED REQUEST & RESPONSE {}\n".format("*" * 32, "*" * 32)

                    # log request
                    err_msg += "====== request details ======\n"
                    logger.error(str(parsed_request_dict))

                    # log response
                    logger.error(str(resp_obj.resp_obj))

            try:
                validate_list, failures_string = resp_obj.validate(
                    validators, step.variables, self.__project_meta.functions
                )
                if USE_ALLURE:
                    env_name = "step_index" + get_process_thread_id()
                    teststep_index = int(os.environ[env_name]) + 1
                    os.environ[env_name] = str(teststep_index)
                    step_name = 'TestStep-{:03}: '.format(teststep_index) + step.name
                    step_name = parse_data(
                        step_name, step.variables, self.__project_meta.functions
                    )
                    teststep_allure_step(step_name, request_data, response_data, validate_list, step_data.export_vars, setup_hook_list, teardown_hook_list)
                if failures_string:
                    self.__session.data.err_list.append(failures_string)
                    self.__ssh.data.err_list.append(failures_string)
                    raise ValidationFailure(failures_string)
                session_success = True
            except Exception as e:
                error_msg = str(traceback.format_exc())
                session_success = False
                log_req_resp_details()
                self.__duration = time.time() - self.__start_at
                if os.environ.get("use_report2.x") != "true":
                    raise e
            finally:
                self.success = session_success
                step_data.success = session_success

                if hasattr(self.__session, "data") and protocol is None:
                    # vhrun3.client.HttpSession, not locust.clients.HttpSession
                    # save request & response meta data
                    self.__session.data.success = session_success
                    self.__session.data.validators = resp_obj.validation_results
                elif hasattr(self.__ssh, "data") and protocol is not None:
                    self.__ssh.data.success = session_success
                    self.__ssh.data.validators = resp_obj.validation_results
        except Exception as e:
            error_msg = str(traceback.format_exc())
            self.__session.data.err_list.append(error_msg)
            self.__ssh.data.err_list.append(error_msg)
            raise e
        finally:
            if hasattr(self.__session, "data") and protocol is None:
                step_data.data = copy.deepcopy(self.__session.data)
            elif hasattr(self.__ssh, "data") and protocol is not None:
                step_data.data = copy.deepcopy(self.__ssh.data)
            if step_data.data.err_list:
                step_data.data.attachment = "\n".join(step_data.data.err_list)
                step_data.data.err_list = []
            # 这句很重要，不然attachment会影响别的case
            self.__ssh.data.err_list = self.__session.data.err_list = []
            self.__ssh.data.attachment = self.__session.data.attachment = ''

        return step_data

    def __run_step_testcase(self, step: TStep) -> StepData:
        """run teststep: referenced testcase"""
        step_data = StepData(name=step.name)
        step_variables = step.variables
        step_export = step.export

        # setup hooks
        if step.setup_hooks:
            self.__call_hooks(step.setup_hooks, step_variables, "setup testcase")

        if hasattr(step.testcase, "config") and hasattr(step.testcase, "teststeps"):
            testcase_cls = step.testcase
            case_result = (
                testcase_cls()
                    .with_session(self.__session)
                    .with_case_id(self.__case_id)
                    .with_variables(step_variables)
                    .with_export(step_export)
                    .run()
            )

        elif isinstance(step.testcase, Text):
            if os.path.isabs(step.testcase):
                ref_testcase_path = step.testcase
            else:
                ref_testcase_path = os.path.join(
                    self.__project_meta.RootDir, step.testcase
                )

            case_result = (
                HttpRunner()
                    .with_session(self.__session)
                    .with_case_id(self.__case_id)
                    .with_variables(step_variables)
                    .with_export(step_export)
                    .run_path(ref_testcase_path)
            )

        else:
            raise exceptions.ParamsError(
                f"Invalid teststep referenced testcase: {step.dict()}"
            )

        # teardown hooks
        if step.teardown_hooks:
            self.__call_hooks(step.teardown_hooks, step.variables, "teardown testcase")

        step_data.data = case_result.get_step_datas()  # list of step data
        step_data.export_vars = case_result.get_export_variables()
        step_data.success = case_result.success
        self.success = case_result.success

        if step_data.export_vars:
            logger.info(f"export variables: {step_data.export_vars}")

        return step_data

    def __run_step(self, step: TStep) -> Dict:
        """run teststep, teststep maybe a request or referenced testcase"""
        logger.info(f"run step begin: {step.name} >>>>>>")

        protocol = step.protocol

        if step.request or protocol == "ssh":
            step_data = self.__run_step_request(step, protocol)
        elif step.testcase:
            step_data = self.__run_step_testcase(step)
        else:
            raise ParamsError(
                f"teststep is neither a request nor a referenced testcase: {step.dict()}"
            )
        self.__step_datas.append(step_data)
        logger.info(f"run step end: {step.name} <<<<<<\n")
        return step_data.export_vars

    def __parse_config(self, config: TConfig) -> NoReturn:

        config.variables.update(self.__session_variables)
        config.variables = parse_variables_mapping(
            config.variables, self.__project_meta.functions
        )
        config.name = parse_data(
            config.name, config.variables, self.__project_meta.functions
        )
        config.base_url = parse_data(
            config.base_url, config.variables, self.__project_meta.functions
        )

    def run_testcase(self, testcase: TestCase) -> "HttpRunner":
        """run specified testcase

        Examples:
            >>> testcase_obj = TestCase(config=TConfig(...), teststeps=[TStep(...)])
            >>> HttpRunner().with_project_meta(project_meta).run_testcase(testcase_obj)

        """
        self.__config = testcase.config
        self.__teststeps = testcase.teststeps

        # prepare
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__parse_config(self.__config)
        self.__start_at = time.time()
        self.__step_datas: List[StepData] = []
        self.__session = self.__session or HttpSession()
        # save extracted variables of teststeps
        extracted_variables: VariablesMapping = {}

        if self.__config.skip_if_list:
            skip_result: dict = self.__call_skip_if(self.__config.skip_if_list, self.__config.variables,
                                                    "*** skipIf testcase ***")
            skip_flag = True if True in list(skip_result.values()) else False
            if skip_flag:
                skip_msg = "\n Skip Testcase: {} \n Skip Detail -> {} \n".format(self.__config.name, str(skip_result))
                logger.info(skip_msg)
                pytest.skip(skip_msg)

        if self.__config.setup_hooks:
            self.__call_hooks(self.__config.setup_hooks, self.__config.variables, "setup testcase")

        # run teststeps
        for step in self.__teststeps:
            # override variables
            # step variables > extracted variables from previous steps
            step.variables = merge_variables(step.variables, extracted_variables)
            # step variables > testcase config variables
            step.variables = merge_variables(step.variables, self.__config.variables)

            # parse variables
            step.variables = parse_variables_mapping(
                step.variables, self.__project_meta.functions
            )

            # run step
            if step.skip_if_list:
                skip_result: dict = self.__call_skip_if(step.skip_if_list, step.variables,
                                                        "<<<< skipIf teststep: {} >>>".format(step.name))
                skip_flag = True if True in list(skip_result.values()) else False
                if skip_flag:
                    logger.info("\n Skip TestStep: {} \n Skip Detail -> {}\n".format(step.name, str(skip_result)))
                    continue

            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            step_name = copy.deepcopy(step.name)
            # loop_while init
            loop_flag = step.loop_while.get("loop_flag")
            gap_time = step.loop_while.get("gap_time")
            timeout = step.loop_while.get("timeout")
            try:
                env_name = loop_flag + get_process_thread_id()
                while_flag = os.environ[env_name]
            except Exception:
                while_flag = "false"
            # loop_for init
            for_flag = True if step.loop_for.get("iter_values") else False

            extract_mapping = {}
            if while_flag != "true" and not for_flag:
                extract_mapping = self.__run_step(step)
            elif for_flag:  # run loop for
                iter_values = parse_data(
                    step.loop_for.get("iter_values"), step.variables, self.__project_meta.functions
                )
                loop = False
                for item in iter_values:
                    step.name = step_name + " --> iter_value: {}".format(item)
                    if loop:
                        env_name = "step_index" + get_process_thread_id()
                        teststep_index = os.environ[env_name]
                        os.environ[env_name] = str(int(teststep_index) - 1)
                    step_var = step.loop_for.get("step_var")
                    if step_var:
                        step.variables.update({step_var: item})
                    extract_mapping = self.__run_step(step)
                    loop = True
            else:   # run loop while
                start_time = time.time()
                iter_index = 0
                loop = False
                while while_flag == "true":
                    step.name = step_name + " --> iter_index: {}".format(iter_index)
                    if loop:
                        env_name = "step_index" + get_process_thread_id()
                        teststep_index = os.environ[env_name]
                        os.environ[env_name] = str(int(teststep_index) - 1)
                    extract_mapping = self.__run_step(step)
                    if time.time() - start_time >= float(timeout):
                        break
                    else:
                        iter_index += 1
                        loop = True  # 进入循环执行第一次后，进入下一次就得用同一个index了
                    # 检测flag是否变化
                    try:
                        env_name = loop_flag + get_process_thread_id()
                        while_flag = os.environ[env_name]
                    except Exception:
                        while_flag = "false"
                    # flag没变就要延时
                    if while_flag == "true":
                        time.sleep(float(gap_time))
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            # save extracted variables to session variables
            extracted_variables.update(extract_mapping)

        self.__session_variables.update(extracted_variables)
        self.__duration = time.time() - self.__start_at

        if self.__config.teardown_hooks:
            self.__call_hooks(self.__config.teardown_hooks, self.__config.variables, "teardown testcacse")


        return self

    def run_path(self, path: Text) -> "HttpRunner":
        if not os.path.isfile(path):
            raise exceptions.ParamsError(f"Invalid testcase path: {path}")

        testcase_obj = load_testcase_file(path)
        return self.run_testcase(testcase_obj)

    def run(self) -> "HttpRunner":
        """ run current testcase

        Examples:
            >>> TestCaseRequestWithFunctions().run()

        """
        self.__init_tests__()
        testcase_obj = TestCase(config=self.__config, teststeps=self.__teststeps)
        return self.run_testcase(testcase_obj)

    def get_step_datas(self) -> List[StepData]:
        return self.__step_datas

    def get_export_variables(self) -> Dict:
        # override testcase export vars with step export
        export_var_names = self.__export or self.__config.export
        export_vars_mapping = {}
        for var_name in export_var_names:
            if var_name not in self.__session_variables:
                raise ParamsError(
                    f"failed to export variable {var_name} from session variables {self.__session_variables}"
                )

            export_vars_mapping[var_name] = self.__session_variables[var_name]

        return export_vars_mapping

    def get_summary(self) -> TestCaseSummary:
        """get testcase result summary"""
        start_at_timestamp = self.__start_at
        start_at_iso_format = datetime.utcfromtimestamp(start_at_timestamp).isoformat()
        return TestCaseSummary(
            name=self.__config.name,
            success=self.success,
            case_id=self.__case_id,
            time=TestCaseTime(
                start_at=self.__start_at,
                start_at_iso_format=start_at_iso_format,
                duration=self.__duration,
            ),
            in_out=TestCaseInOut(
                config_vars=self.__config.variables,
                export_vars=self.get_export_variables(),
            ),
            log=self.__log_path,
            step_datas=self.__step_datas,
        )

    def start_run(self, param: Dict = None) -> "HttpRunner":
        """main entrance, discovered by pytest"""
        env_name = "step_index" + get_process_thread_id()
        os.environ[env_name] = "0"

        self.__init_tests__()
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__case_id = self.__case_id or str(uuid.uuid4())

        if "start_time" in os.environ:
            self.__log_path = self.__log_path or os.path.join(
                self.__project_meta.RootDir, "logs", "{}.run.log".format(os.environ["start_time"])
            )
        else:
            self.__log_path = self.__log_path or os.path.join(
                self.__project_meta.RootDir, "logs", f"{self.__case_id}.run.log"
            )
        log_handler = logger.add(self.__log_path, level="DEBUG")

        # parse config name
        config_variables = self.__config.variables
        if param:
            config_variables.update(param)
        config_variables.update(self.__session_variables)
        self.__config.name = parse_data(
            self.__config.name, config_variables, self.__project_meta.functions
        )

        if USE_ALLURE:
            # update allure report meta
            allure.dynamic.title(self.__config.name)
            allure.dynamic.description(f"TestCase ID: {self.__case_id}")

        logger.info(
            f"Start to run testcase: {self.__config.name}, TestCase ID: {self.__case_id}"
        )

        try:
            return self.run_testcase(
                TestCase(config=self.__config, teststeps=self.__teststeps)
            )
        finally:
            env_name = "step_index" + get_process_thread_id()
            os.environ[env_name] = "0"
            logger.remove(log_handler)
            logger.info(f"generate testcase log: {self.__log_path}")
            if os.environ.get("use_report2.x") == "true":
                error_msg = ""
                try:
                    summary = self.get_summary()
                except Exception:
                    error_msg += str(traceback.format_exc())
                    summary = TestCaseSummary(
                        name=self.__config.name,
                        success=self.success,
                        case_id=self.__case_id,
                        time=TestCaseTime(
                            start_at=self.__start_at,
                            duration=self.__duration,
                        ),
                        log=self.__log_path,
                        step_datas=self.__step_datas,
                    )
                relative_path = self.config.path.split(self.__project_meta.RootDir)[-1][1:]
                error_msg += str(traceback.format_exc())
                aggregated_summary, traceback_msg = aggregate(summary, relative_path, error_msg=error_msg)
                case_summary_list.append(aggregated_summary)
                if traceback_msg:
                    raise Exception(traceback_msg)
