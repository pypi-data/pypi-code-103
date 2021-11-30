"""
LogClient class is the main class in the SDK. It can be used to communicate with
log service server to put/get data.

:Author: Aliyun
"""

import json
import six
import zlib
from datetime import datetime
import logging
import locale

from .logclient_core import make_lcrud_methods
from .logexception import LogException
from .putlogsresponse import PutLogsResponse
from .util import Util,  base64_encodestring as b64e
from .version import API_VERSION, USER_AGENT

from .log_logs_raw_pb2 import LogGroupRaw as LogGroup
import struct

logger = logging.getLogger(__name__)

try:
    import lz4

    if not hasattr(lz4, 'loads') or not hasattr(lz4, 'dumps'):
        lz4 = None
    else:
        def lz_decompress(raw_size, data):
            return lz4.loads(struct.pack('<I', raw_size) + data)

        def lz_compresss(data):
            return lz4.dumps(data)[4:]

except ImportError:
    lz4 = None


MAX_LIST_PAGING_SIZE = 500
MAX_GET_LOG_PAGING_SIZE = 100

DEFAULT_QUERY_RETRY_COUNT = 10
DEFAULT_QUERY_RETRY_INTERVAL = 0.2


def _apply_cn_keys_patch():
    """
    apply this patch due to an issue in http.client.parse_headers
    when there're multi-bytes in headers. it will truncate some headers.
    https://github.com/aliyun/aliyun-log-python-sdk/issues/79
    """
    import sys
    if sys.version_info[:2] == (3, 5):
        import http.client as hc
        old_parse = hc.parse_headers

        def parse_header(*args, **kwargs):
            fp = args[0]
            old_readline = fp.readline

            def new_readline(*args, **kwargs):
                ret = old_readline(*args, **kwargs)
                if ret.lower().startswith(b'x-log-query-info'):
                    return b'x-log-query-info: \r\n'
                return ret

            fp.readline = new_readline

            ret = old_parse(*args, **kwargs)
            return ret

        hc.parse_headers = parse_header


_apply_cn_keys_patch()


class LogClient(object):
    """ Construct the LogClient with endpoint, accessKeyId, accessKey.

    :type endpoint: string
    :param endpoint: log service host name, for example, ch-hangzhou.log.aliyuncs.com or https://cn-beijing.log.aliyuncs.com

    :type accessKeyId: string
    :param accessKeyId: aliyun accessKeyId

    :type accessKey: string
    :param accessKey: aliyun accessKey
    """

    __version__ = API_VERSION
    Version = __version__

    def __init__(self, request_session, endpoint, accessKeyId, accessKey, securityToken=None, source=None, timeout=30):
        self._isRowIp = Util.is_row_ip(endpoint)
        self._setendpoint(endpoint)
        self._accessKeyId = accessKeyId
        self._accessKey = accessKey
        self._timeout = timeout
        self._request_session = request_session
        if source is None:
            self._source = Util.get_host_ip(self._logHost)
        else:
            self._source = source
        self._securityToken = securityToken

        self._user_agent = USER_AGENT

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    def set_user_agent(self, user_agent):
        """
        set user agent

        :type user_agent: string
        :param user_agent: user agent

        :return: None

        """
        self._user_agent = user_agent

    def _setendpoint(self, endpoint):
        self.http_type = 'http://'
        self._port = 80

        endpoint = endpoint.strip()
        pos = endpoint.find('://')
        if pos != -1:
            self.http_type = endpoint[:pos + 3]
            endpoint = endpoint[pos + 3:]

        if self.http_type.lower() == 'https://':
            self._port = 443

        pos = endpoint.find('/')
        if pos != -1:
            endpoint = endpoint[:pos]
        pos = endpoint.find(':')
        if pos != -1:
            self._port = int(endpoint[pos + 1:])
            endpoint = endpoint[:pos]
        self._logHost = endpoint
        self._endpoint = endpoint + ':' + str(self._port)

    @staticmethod
    def _getGMT():
        try:
            locale.setlocale(locale.LC_TIME, "C")
        except Exception as ex:
            logger.warning("failed to set locale time to C. skip it: {0}".format(ex))
        return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    @staticmethod
    def _loadJson(resp_status, resp_header, resp_body, requestId):
        if not resp_body:
            return None
        try:
            if isinstance(resp_body, six.binary_type):
                return json.loads(resp_body.decode('utf8', "ignore"))

            return json.loads(resp_body)
        except Exception as ex:
            raise LogException('BadResponse',
                               'Bad json format:\n"%s"' % b64e(resp_body) + '\n' + repr(ex),
                               requestId, resp_status, resp_header, resp_body)

    def _getHttpResponse(self, method, url, params, body, headers):  # ensure method, url, body is str
        try:
            headers['User-Agent'] = self._user_agent
            r = getattr(self._request_session, method.lower())(url, params=params, data=body,
                                                               headers=headers, timeout=self._timeout)
            return r.status_code, r.content, r.headers
        except Exception as ex:
            raise LogException('LogRequestError', str(ex))

    def _sendRequest(self, method, url, params, body, headers, respons_body_type='json'):
        (resp_status, resp_body, resp_header) = self._getHttpResponse(method, url, params, body, headers)
        header = {}
        for key, value in resp_header.items():
            header[key] = value

        requestId = Util.h_v_td(header, 'x-log-requestid', '')

        if resp_status == 200:
            if respons_body_type == 'json':
                exJson = self._loadJson(resp_status, resp_header, resp_body, requestId)
                exJson = Util.convert_unicode_to_str(exJson)
                return resp_status, exJson, header
            else:
                return resp_status, resp_body, header

        exJson = self._loadJson(resp_status, resp_header, resp_body, requestId)
        exJson = Util.convert_unicode_to_str(exJson)

        if 'errorCode' in exJson and 'errorMessage' in exJson:
            raise LogException(exJson['errorCode'], exJson['errorMessage'], requestId,
                               resp_status, resp_header, resp_body)
        else:
            exJson = '. Return json is ' + str(exJson) if exJson else '.'
            raise LogException('LogRequestError',
                               'Request is failed. Http code is ' + str(resp_status) + exJson, requestId,
                               resp_status, resp_header, resp_body)

    def _send(self, method, project, body, resource, params, headers, respons_body_type='json'):
        if body:
            headers['Content-Length'] = str(len(body))
            headers['Content-MD5'] = Util.cal_md5(body)
        else:
            headers['Content-Length'] = '0'
            headers["x-log-bodyrawsize"] = '0'

        headers['x-log-apiversion'] = API_VERSION
        headers['x-log-signaturemethod'] = 'hmac-sha1'
        if self._isRowIp or not project:
            url = self.http_type + self._endpoint
        else:
            url = self.http_type + project + "." + self._endpoint

        if project:
            headers['Host'] = project + "." + self._logHost
        else:
            headers['Host'] = self._logHost

        headers['Date'] = self._getGMT()

        if self._securityToken:
            headers["x-acs-security-token"] = self._securityToken

        signature = Util.get_request_authorization(method, resource,
                                                   self._accessKey, params, headers)

        headers['Authorization'] = "LOG " + self._accessKeyId + ':' + signature
        headers['x-log-date'] = headers['Date']  # bypass some proxy doesn't allow "Date" in header issue.
        url = url + resource

        return self._sendRequest(method, url, params, body, headers, respons_body_type)

    @staticmethod
    def _get_unicode(key):
        if isinstance(key, six.binary_type):
            try:
                key = key.decode('utf-8')
            except UnicodeDecodeError:
                return key
        return key

    @staticmethod
    def _get_binary(key):
        if isinstance(key, six.text_type):
            return key.encode('utf-8')
        return key

    def set_source(self, source):
        """
        Set the source of the log client

        :type source: string
        :param source: new source

        :return: None
        """
        self._source = source

    def put_log_raw(self, project, logstore, log_group, compress=None):
        """ Put logs to log service. using raw data in protobuf

        :type project: string
        :param project: the Project name

        :type logstore: string
        :param logstore: the logstore name

        :type log_group: LogGroup
        :param log_group: log group structure

        :type compress: boolean
        :param compress: compress or not, by default is True

        :return: PutLogsResponse

        :raise: LogException
        """
        body = log_group.SerializeToString()
        raw_body_size = len(body)
        headers = {'x-log-bodyrawsize': str(raw_body_size), 'Content-Type': 'application/x-protobuf'}

        if compress is None or compress:
            if lz4:
                headers['x-log-compresstype'] = 'lz4'
                body = lz_compresss(body)
            else:
                headers['x-log-compresstype'] = 'deflate'
                body = zlib.compress(body)

        params = {}
        resource = '/logstores/' + logstore + "/shards/lb"

        (status_code, resp, header) = self._send('POST', project, body, resource, params, headers)

        return PutLogsResponse(status_code, header, resp)

    def put_logs(self, request):
        """ Put logs to log service. up to 512000 logs up to 10MB size
        Unsuccessful opertaion will cause an LogException.
        
        :type request: PutLogsRequest
        :param request: the PutLogs request parameters class
        
        :return: PutLogsResponse

        :raise: LogException
        """
        if len(request.get_log_items()) > 512000:
            raise LogException('InvalidLogSize',
                               "logItems' length exceeds maximum limitation: 512000 lines. now: {0}".format(
                                   len(request.get_log_items())))
        logGroup = LogGroup()
        logGroup.Topic = request.get_topic()
        if request.get_source():
            logGroup.Source = request.get_source()
        else:
            if self._source == '127.0.0.1':
                self._source = Util.get_host_ip(request.get_project() + '.' + self._logHost)
            logGroup.Source = self._source
        for logItem in request.get_log_items():
            log = logGroup.Logs.add()
            log.Time = logItem.get_time()
            contents = logItem.get_contents()
            for key, value in contents:
                content = log.Contents.add()
                content.Key = self._get_unicode(key)
                content.Value = self._get_binary(value)
        if request.get_log_tags() is not None:
            tags = request.get_log_tags()
            for key, value in tags:
                pb_tag = logGroup.LogTags.add()
                pb_tag.Key = key
                pb_tag.Value = value
        body = logGroup.SerializeToString()

        if len(body) > 10 * 1024 * 1024:  # 10 MB
            raise LogException('InvalidLogSize',
                               "logItems' size exceeds maximum limitation: 10 MB. now: {0} MB.".format(
                                   len(body) / 1024.0 / 1024))

        headers = {'x-log-bodyrawsize': str(len(body)), 'Content-Type': 'application/x-protobuf'}
        is_compress = request.get_compress()

        compress_data = None
        if is_compress:
            if lz4:
                headers['x-log-compresstype'] = 'lz4'
                compress_data = lz_compresss(body)
            else:
                headers['x-log-compresstype'] = 'deflate'
                compress_data = zlib.compress(body)

        params = {}
        logstore = request.get_logstore()
        project = request.get_project()
        if request.get_hash_key() is not None:
            resource = '/logstores/' + logstore + "/shards/route"
            params["key"] = request.get_hash_key()
        else:
            resource = '/logstores/' + logstore + "/shards/lb"

        if is_compress:
            (status_code, resp, header) = self._send('POST', project, compress_data, resource, params, headers)
        else:
            (status_code, resp, header) = self._send('POST', project, body, resource, params, headers)

        return PutLogsResponse(status_code, header, resp)


make_lcrud_methods(LogClient, 'dashboard', name_field='dashboardName')
make_lcrud_methods(LogClient, 'alert', name_field='name', root_resource='/jobs', entities_key='results')
make_lcrud_methods(LogClient, 'savedsearch', name_field='savedsearchName')
make_lcrud_methods(LogClient, 'shipper', logstore_level=True, root_resource='/shipper', name_field='shipperName')

