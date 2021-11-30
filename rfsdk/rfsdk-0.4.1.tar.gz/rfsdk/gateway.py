# -*- coding: utf-8 -*-
import os
import ant

from rfsdk.protocol.service_method import *


class Gateway(object):
    SERVER_NAME = 'rfsdk_gateway'

    def __init__(self, ip, port, conf=ant.GlobalConf()):
        self._ip = ip
        self._port = port
        self._client = None
        self._server = None
        self._option = ant.Option()
        self._protocol_head = None
        self._service_name = SERVICE_GATEWAY
        self._use_verbose_log = True
        self._is_console_log = True
        self._log_dir = os.path.join(os.path.dirname(os.getcwd()) + '/log')

    def connect(self):
        gateway_auth = ant.GatewayAuthenticator()
        ant.init_gateway_auth(gateway_auth, self._ip)

        self._client = ant.Client(name=self._service_name, need_ns=False, auth=gateway_auth)
        self._client.set_used_verbose_log(self._use_verbose_log)

        ep = ant.Endpoint()
        ep.set_communication_type(ant.CommunicationType.kCommunicationTcp)
        ep.set_ip(self._ip)
        ep.set_port(self._port)
        ep.set_protocol(ant.ProtocolType.kProtocolGateway)
        ep.set_required_auth(True)

        self._client.append_endpoint(ep)

        self._client.set_on_create_channel(
            lambda conn: conn.get_codec().set_protocol_head(self._protocol_head))

        if self._server is None:
            self._server = ant.Server.instance(Gateway.SERVER_NAME)
            self._server.set_log_dir(self._is_console_log, self._log_dir)
            self._server.start(conf=ant.GlobalConf())

        self._server.add_client(self._client)

        if self._client.sync_auth():
            return True
        else:
            ant.log_err('gateway auth failed!')
            return False

    def wait(self):
        self._server.wait()

    def set_log_dir(self, is_console_log, log_dir):
        self._is_console_log = is_console_log
        if log_dir is not None:
            self._log_dir = log_dir

    def set_protocol_head(self, protocol_head):
        self._protocol_head = protocol_head

    def set_default_service_name(self, service_name):
        self._service_name = service_name

    def set_used_verbose_log(self, need_log):
        self._use_verbose_log = need_log

    def get_server(self):
        return self._server

    def get_client(self):
        return self._client

    def gateway_call(self, service, method, req):
        self._option.set_forward_service_name(service)
        ret, rsp = ant.call(self._service_name, method, req, self._option)
        if method is METHOD_ACCOUNT_LOGIN and ret == 0:
            investor_key = str(rsp['login']['investor_key'])
            channel_key = investor_key[0:-2]
            interface_type = int(investor_key[1:3])
            service_type = 2 ** interface_type
            self._option.set_channel_key(channel_key)
            self._option.set_service_type(service_type)

        return ret, rsp

    def gateway_call_mf(self, service, method, req):
        self._option.set_forward_service_name(service)
        return ant.call_mf(self._service_name, method, req, self._option)
