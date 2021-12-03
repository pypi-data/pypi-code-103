import json
import time

import requests
import urllib3
from loguru import logger
from requests import Request, Response
from requests.exceptions import (
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    RequestException,
)

from vhrun3.models import RequestData, ResponseData
from vhrun3.models import SessionData, ReqRespData
from vhrun3.utils import lower_dict_keys, omit_long_data

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiResponse(Response):
    def raise_for_status(self):
        if hasattr(self, "error") and self.error:
            raise self.error
        Response.raise_for_status(self)


def get_req_resp_record(resp_obj: Response) -> ReqRespData:
    """ get request and response info from Response() object.
    """

    def log_print(req_or_resp, r_type):
        msg = f"\n================== {r_type} details ==================\n"
        for key, value in req_or_resp.dict().items():
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, indent=4, ensure_ascii=False)

            msg += "{:<8} : {}\n".format(key, value)
        logger.debug(msg)

    # record actual request info
    request_headers = dict(resp_obj.request.headers)
    request_cookies = resp_obj.request._cookies.get_dict()

    request_body = resp_obj.request.body
    if request_body is not None:
        try:
            request_body = json.loads(request_body)
        except json.JSONDecodeError:
            # str: a=1&b=2
            pass
        except UnicodeDecodeError:
            # bytes/bytearray: request body in protobuf
            pass
        except TypeError:
            # neither str nor bytes/bytearray, e.g. <MultipartEncoder>
            pass

        request_content_type = lower_dict_keys(request_headers).get("content-type")
        if request_content_type and "multipart/form-data" in request_content_type:
            # upload file type
            request_body = "upload file stream (OMITTED)"

    request_data = RequestData(
        method=resp_obj.request.method,
        url=resp_obj.request.url,
        headers=request_headers,
        cookies=request_cookies,
        body=request_body,
    )

    # log request details in debug mode
    log_print(request_data, "request")

    # record response info
    resp_headers = dict(resp_obj.headers)
    lower_resp_headers = lower_dict_keys(resp_headers)
    content_type = lower_resp_headers.get("content-type", "")

    if "image" in content_type:
        # response is image type, record bytes content only
        response_body = resp_obj.content
    else:
        try:
            # try to record json data
            response_body = resp_obj.json()
        except ValueError:
            # only record at most 512 text charactors
            resp_text = resp_obj.text
            response_body = omit_long_data(resp_text)

    response_data = ResponseData(
        status_code=resp_obj.status_code,
        cookies=resp_obj.cookies or {},
        encoding=resp_obj.encoding,
        headers=resp_headers,
        content_type=content_type,
        body=response_body,
    )

    # log response details in debug mode
    log_print(response_data, "response")

    req_resp_data = ReqRespData(request=request_data, response=response_data)
    return req_resp_data


class HttpSession(requests.Session):
    """
    Class for performing HTTP requests and holding (session-) cookies between requests (in order
    to be able to log in and out of websites). Each request is logged so that HttpRunner can
    display statistics.

    This is a slightly extended version of `python-request <http://python-requests.org>`_'s
    :py:class:`requests.Session` class and mostly this class works exactly the same.
    """

    def __init__(self):
        super(HttpSession, self).__init__()
        self.data = SessionData()

    def update_last_req_resp_record(self, resp_obj):
        """
        update request and response info from Response() object.
        """
        # TODO: fix
        self.data.req_resps.pop()
        self.data.req_resps.append(get_req_resp_record(resp_obj))

    def request(self, method, url, name=None, **kwargs):
        """
        Constructs and sends a :py:class:`requests.Request`.
        Returns :py:class:`requests.Response` object.

        :param method:
            method for the new :class:`Request` object.
        :param url:
            URL for the new :class:`Request` object.
        :param name: (optional)
            Placeholder, make compatible with Locust's HttpSession
        :param params: (optional)
            Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param data: (optional)
            Dictionary or bytes to send in the body of the :class:`Request`.
        :param headers: (optional)
            Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional)
            Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional)
            Dictionary of ``'filename': file-like-objects`` for multipart encoding upload.
        :param auth: (optional)
            Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional)
            How long to wait for the server to send data before giving up, as a float, or \
            a (`connect timeout, read timeout <user/advanced.html#timeouts>`_) tuple.
            :type timeout: float or tuple
        :param allow_redirects: (optional)
            Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional)
            Dictionary mapping protocol to the URL of the proxy.
        :param stream: (optional)
            whether to immediately download the response content. Defaults to ``False``.
        :param verify: (optional)
            if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        :param cert: (optional)
            if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        """
        self.data = SessionData()

        # timeout default to 120 seconds
        kwargs.setdefault("timeout", 120)

        # set stream to True, in order to get client/server IP/Port
        kwargs["stream"] = True

        start_timestamp = time.time()
        response = self._send_request_safe_mode(method, url, **kwargs)
        response_time_ms = round((time.time() - start_timestamp) * 1000, 2)

        try:
            client_ip, client_port = response.raw.connection.sock.getsockname()
            self.data.address.client_ip = client_ip
            self.data.address.client_port = client_port
            logger.debug(f"client IP: {client_ip}, Port: {client_port}")
        except AttributeError as ex:
            logger.warning(f"failed to get client address info: {ex}")

        try:
            server_ip, server_port = response.raw.connection.sock.getpeername()
            self.data.address.server_ip = server_ip
            self.data.address.server_port = server_port
            logger.debug(f"server IP: {server_ip}, Port: {server_port}")
        except AttributeError as ex:
            logger.warning(f"failed to get server address info: {ex}")

        # get length of the response content
        content_size = int(dict(response.headers).get("content-length") or 0)

        # record the consumed time
        self.data.stat.response_time_ms = response_time_ms
        self.data.stat.elapsed_ms = response.elapsed.microseconds / 1000.0
        self.data.stat.content_size = content_size

        # record request and response histories, include 30X redirection
        response_list = response.history + [response]
        self.data.req_resps = [
            get_req_resp_record(resp_obj) for resp_obj in response_list
        ]

        try:
            response.raise_for_status()
        except RequestException as ex:
            logger.error(f"{str(ex)}")
        else:
            logger.info(
                f"status_code: {response.status_code}, "
                f"response_time(ms): {response_time_ms} ms, "
                f"response_length: {content_size} bytes"
            )

        return response

    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send a HTTP request, and catch any exception that might occur due to connection problems.
        Safe mode has been removed from requests 1.x.
        """
        try:
            return requests.Session.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as ex:
            resp = ApiResponse()
            resp.error = ex
            resp.status_code = 0  # with this status_code, content returns None
            resp.request = Request(method, url).prepare()
            return resp


import time
import paramiko
from vhrun3.models import SessionData


class SSH:
    def __init__(self):
        self.ip = None
        self.user = None
        self.password = None
        self.ssh = None
        self.connection = {}
        self.port = None
        self.init_meta_data()
        self.data: SessionData = SessionData()

    def init_meta_data(self):
        """ initialize meta_data, it will store detail data of request and response
        """
        self.meta_data = {
            "name": "",
            "data": [
                {
                    "request": {
                        "executor": "N/A",
                        "params": "N/A",
                    },
                    "response": {

                    }
                }
            ],
            "stat": {
                "content_size": "N/A",
                "elapsed_ms": "N/A",
            }
        }

    def update_last_req_resp_record(self, resp_obj):
        """
        update request and response info from Response() object.
        """
        self.meta_data["data"].pop()
        self.meta_data["data"].append(resp_obj)

    def request(self,connection, ssh_type, fields, name=None, **kwargs):
        """
        :param executor:
            shell commond or execut
        :param params:
            params of executor
        :param name: (optional)

        if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        """
        self.init_meta_data()

        # record test name
        self.meta_data["name"] = name
        self.meta_data["data"] = [{"request": {}, "response": {}}]

        # record original request info
        request = self.meta_data["data"][0]["request"]
        request.update({"SSH": connection})
        if "params" in fields:
            params = fields.get("params")
            if isinstance(params, list):
                fields["params"] = ' '.join(params)
        request.update(fields)


        self.connection = connection
        start_timestamp = time.time()
        if ssh_type == "shell":
            executor = fields.get("executor")
            params = fields.get("params")
            cmd = "{} {}".format(executor, params)
            try:
                response = self.run_cmd(cmd)
            except Exception as e:
                import traceback, sys
                response = {"stdout": "", "stderr": traceback.format_exc()}
        elif ssh_type == "upload":
            local_path = fields.get("local_path")
            remote_path = fields.get("remote_path")
            response = self.upload_file(local_path, remote_path, port=connection.get("port"))
        elif ssh_type == "download":
            remote_path = fields.get("remote_path")
            local_path = fields.get("local_path")
            response = self.download_file(remote_path, local_path, port=connection.get("port"))
        elapsed_ms = round((time.time() - start_timestamp) * 1000, 2)

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body


        # record the consumed time
        content_size = len(str(response))
        self.meta_data["stat"] = {"elapsed_ms": elapsed_ms, "content_size": content_size}

        self.meta_data["data"][0]["response"] = {"response": response}


        resp = {"request": request, "body": response}

        return resp

    def conn(self, **kwargs):
        self.ip = kwargs.get("hostname")
        self.port = kwargs.get("port")
        self.user = kwargs.get("username")
        self.password = kwargs.get("password")
        for _ in range(0, 5):
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self.ssh.connect(timeout=_ + 1, **kwargs)
            except Exception as e:
                print(f"主机{self.ip}连接异常! {e}")
                self.ssh = None
            if self.ssh:
                break
            print(f"{self.ip}连接失败! 重试{_ + 1}次")

    def run_cmd(self, cmd, time_out=10):
        self.conn(**self.connection)
        if self.ssh:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=time_out)
            stdout = stdout.read().decode("utf-8")
            try:
                stdout = json.loads(stdout)
            except Exception as e:
                if "\n" in stdout:
                    stdout = [item for item in stdout.split('\n')  if item]
            stderr = stderr.read().decode("utf-8")
            try:
                stderr = json.loads(stderr.read().decode("utf-8"))
            except Exception as e:
                if "\n" in stderr:
                    stderr = [item for item in stderr.split('\n') if item]
            ret = {"stdout": stdout, "stderr": stderr}
        else:
            ret = "SSH Connetion Fail!"
        self.ssh.close()
        return ret

    def connect_withtrans(self, port):
        # 连接一个trans 通道， 用来上传和下载文件
        transport = paramiko.Transport(self.ip+':'+str(port))
        transport.connect(username=self.user, password=self.password)
        self.__transport= transport

    def upload_file(self, local_path, remote_path, port=22):
        try:
            self.conn(**self.connection)
            # 向远程服务器上传一个文件
            self.connect_withtrans(port)
            # sftp.chmod(target_path, 0o755)
            sftp = paramiko.SFTPClient.from_transport(self.__transport)
            sftp.put(local_path, remote_path, confirm=True)
            sftp.chmod(remote_path, 0o755)
            sftp.close()
            return {"stdout": "OK", "stderr": ''}
        except Exception as e:
            return {"stdout": "", "stderr": str(e)}
        finally:
            self.ssh.close()

    def download_file(self, remote_path, local_path, port=22):
        try:
            self.conn(**self.connection)
            # 向远程服务器下载一个文件
            self.connect_withtrans(port)
            sftp = paramiko.SFTPClient.from_transport(self.__transport)
            sftp.get(remote_path, local_path)
            sftp.close()
            return {"stdout": "OK", "stderr": ''}
        except Exception as e:
            return {"stdout": "", "stderr": str(e)}
        finally:
            self.ssh.close()

    def close(self):
        if self.ssh:
            self.ssh.close()