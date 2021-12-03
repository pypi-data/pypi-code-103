from aio_pika import connect_robust, IncomingMessage, Message
from aio_pika.patterns import RPC
import asyncio
import uuid
from . import MythicCommandBase
import json
import base64
import pathlib
import sys

connection = None
#channel = None
#callback_queue = None
#futures = {}
rpc = None

class RPCResponse:
    def __init__(self, resp: dict):
        self._raw_resp = resp
        if resp["status"] == "success":
            self.status = MythicCommandBase.MythicStatus.Success
            self.response = resp["response"] if "response" in resp else ""
            self.error_message = None
        else:
            self.status = MythicCommandBase.MythicStatus.Error
            self.error_message = resp["error"]
            self.response = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, error_message):
        self._error_message = error_message

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    def __str__(self):
        return json.dumps(self._raw_resp)


class MythicFileRPCResponse(RPCResponse):
    def __init__(self, file: RPCResponse):
        super().__init__(file._raw_resp)
        if file.status == MythicCommandBase.MythicStatus.Success:
            self.agent_file_id = file.response["agent_file_id"]
            self.task = file.response["task"]
            self.timestamp = file.response["timestamp"]
            self.deleted = file.response["deleted"]
            self.operator = file.response["operator"]
            self.delete_after_fetch = file.response["delete_after_fetch"]
            self.filename = file.response["filename"]
            self.md5 = file.response["md5"]
            self.sha1 = file.response["sha1"]
            self.chunks_received = file.response["chunks_received"]
            self.total_chunks = file.response["total_chunks"]
            if "contents" in file.response:
                self.contents = base64.b64decode(file.response["contents"])
            else:
                self.contents = None
        else:
            self.agent_file_id = None
            self.task = None
            self.timestamp = None
            self.deleted = None
            self.operator = None
            self.delete_after_fetch = None
            self.filename = None
            self.md5 = None
            self.sha1 = None
            self.chunks_received = None
            self.total_chunks = None
            self.contents = None

    @property
    def agent_file_id(self):
        return self._agent_file_id

    @agent_file_id.setter
    def agent_file_id(self, agent_file_id):
        self._agent_file_id = agent_file_id

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        self._deleted = deleted

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, operator):
        self._operator = operator

    @property
    def delete_after_fetch(self):
        return self._delete_after_fetch

    @delete_after_fetch.setter
    def delete_after_fetch(self, delete_after_fetch):
        self._delete_after_fetch = delete_after_fetch

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def md5(self):
        return self._md5

    @md5.setter
    def md5(self, md5):
        self._md5 = md5

    @property
    def sha1(self):
        return self._sha1

    @sha1.setter
    def sha1(self, sha1):
        self._sha1 = sha1

    @property
    def chunks_received(self):
        return self._chunks_received

    @chunks_received.setter
    def chunks_received(self, chunks_received):
        self._chunks_received = chunks_received

    @property
    def total_chunks(self):
        return self._total_chunks

    @total_chunks.setter
    def total_chunks(self, total_chunks):
        self._total_chunks = total_chunks

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, contents):
        self._contents = contents


class MythicC2RPCResponse(RPCResponse):
    def __init__(self, resp: RPCResponse):
        super().__init__(resp._raw_resp)
        if resp.status == MythicCommandBase.MythicStatus.Success:
            self.data = resp.response
        else:
            self.data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class MythicPayloadRPCResponse(RPCResponse):
    def __init__(self, payload: RPCResponse):
        super().__init__(payload._raw_resp)
        if payload.status == MythicCommandBase.MythicStatus.Success:
            self.uuid = payload.response["uuid"]
            self.tag = payload.response["tag"]
            self.operator = payload.response["operator"]
            self.creation_time = payload.response["creation_time"]
            self.payload_type = payload.response["payload_type"]
            self.operation = payload.response["operation"]
            self.wrapped_payload = payload.response["wrapped_payload"]
            self.deleted = payload.response["deleted"]
            self.auto_generated = payload.response["auto_generated"]
            self.task = payload.response["task"]
            if "contents" in payload.response:
                self.contents = payload.response["contents"]
            self.build_phase = payload.response["build_phase"]
            self.agent_file_id = payload.response["file"]["agent_file_id"]
            self.filename = payload.response["file"]["filename"]
            self.c2info = payload.response["c2info"]
            self.commands = payload.response["commands"]
            self.build_parameters = payload.response["build_parameters"]
        else:
            self.uuid = None
            self.tag = None
            self.operator = None
            self.creation_time = None
            self.payload_type = None
            self.operation = None
            self.wrapped_payload = None
            self.deleted = None
            self.auto_generated = None
            self.task = None
            self.contents = None
            self.build_phase = None
            self.agent_file_id = None
            self.filename = None
            self.c2info = None
            self.commands = None
            self.build_parameters = None

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, operator):
        self._operator = operator

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        self._creation_time = creation_time

    @property
    def payload_type(self):
        return self._payload_type

    @payload_type.setter
    def payload_type(self, payload_type):
        self._payload_type = payload_type

    @property
    def location(self):
        return self._location

    @property
    def operation(self):
        return self._operation

    @operation.setter
    def operation(self, operation):
        self._operation = operation

    @property
    def wrapped_payload(self):
        return self._wrapped_payload

    @wrapped_payload.setter
    def wrapped_payload(self, wrapped_payload):
        self._wrapped_payload = wrapped_payload

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        self._deleted = deleted

    @property
    def auto_generated(self):
        return self._auto_generated

    @auto_generated.setter
    def auto_generated(self, auto_generated):
        self._auto_generated = auto_generated

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, contents):
        try:
            self._contents = base64.b64decode(contents)
        except:
            self._contents = contents

    @property
    def build_phase(self):
        return self._build_phase

    @build_phase.setter
    def build_phase(self, build_phase):
        self._build_phase = build_phase

    @property
    def c2info(self):
        return self._c2info

    @c2info.setter
    def c2info(self, c2info):
        self._c2info = c2info

    @property
    def build_parameters(self):
        return self._build_parameters

    @build_parameters.setter
    def build_parameters(self, build_parameters):
        self._build_parameters = build_parameters

    def set_profile_parameter_value(self,
                                    c2_profile: str,
                                    parameter_name: str,
                                    value: any):
        if self.c2info is None:
            raise Exception("Can't set value when c2 info is None")
        for c2 in self.c2info:
            if c2["name"] == c2_profile:
                c2["parameters"][parameter_name] = value
                return
        raise Exception("Failed to find c2 name")

    def set_build_parameter_value(self,
                                  parameter_name: str,
                                  value: any):
        if self.build_parameters is None:
            raise Exception("Can't set value when build parameters are None")
        for param in self.build_parameters:
            if param["name"] == parameter_name:
                param["value"] = value
                return
        self.build_parameters.append({"name": parameter_name, "value": value})


class MythicResponseRPCResponse(RPCResponse):
    def __init__(self, resp: RPCResponse):
        super().__init__(resp._raw_resp)


class MythicSocksRPCResponse(RPCResponse):
    def __init__(self, socks: RPCResponse):
        super().__init__(socks._raw_resp)


class MythicBaseRPC:
    async def connect(self):
        global connection
        #global channel
        #global callback_queue
        #global futures
        global rpc
        if connection is None:
            config_file = open("rabbitmq_config.json", "rb")
            main_config = json.loads(config_file.read().decode("utf-8"))
            config_file.close()
            connection = await connect_robust(
                host=main_config["host"],
                login=main_config["username"],
                password=main_config["password"],
                virtualhost=main_config["virtual_host"],
            )
            channel = await connection.channel()
            try:
                rpc = await RPC.create(channel)
            except Exception as e:
                print("Failed to create rpc\n" + str(e))
                sys.stdout.flush()
            #callback_queue = await channel.declare_queue(exclusive=True)
            #await callback_queue.consume(self.on_response)
        return self

    #def on_response(self, message: IncomingMessage):
    #    global futures
    #    future = futures.pop(message.correlation_id)
    #    future.set_result(message.body)

    #async def call(self, n, receiver: str = None) -> RPCResponse:
    #    global connection
    #    global futures
    #    global channel
    #    global callback_queue
    #    if connection is None:
    #        await self.connect()
    #    correlation_id = str(uuid.uuid4())
    #    future = self.loop.create_future()

    #    futures[correlation_id] = future
    #    if receiver is None:
    #        router = "rpc_queue"
    #    else:
    #        router = "{}_rpc_queue".format(receiver)
    #    await channel.default_exchange.publish(
    #        Message(
    #            json.dumps(n).encode(),
    #            content_type="application/json",
    #            correlation_id=correlation_id,
    #            reply_to=callback_queue.name,
    #        ),
    #        routing_key=router,
    #    )

     #   return RPCResponse(json.loads(await future))


class MythicRPC(MythicBaseRPC):

    async def get_functions(self) -> RPCResponse:
        global rpc
        await self.connect()
        try:
            output = await rpc.proxy.get_rpc_functions()
            return RPCResponse(output)
        except Exception as e:
            print(str(sys.exc_info()[-1].tb_lineno) +str(e))
            sys.stdout.flush()
            return None

    async def execute(self, function_name: str, **func_kwargs) -> RPCResponse:
        global rpc
        await self.connect()
        try:
            func = getattr(rpc.proxy, function_name)
            if func is not None and callable(func):
                output = await func(task_id=self.task_id, **func_kwargs)
            else:
                output = await rpc.call(function_name, kwargs=dict(task_id=self.task_id,**func_kwargs))
            return RPCResponse(output)
        except Exception as e:
            print(str(sys.exc_info()[-1].tb_lineno) +str(e))
            sys.stdout.flush()
            return None

    async def register_file(
        self,
        file: bytes,
        delete_after_fetch: bool = None,
        saved_file_name: str = None,
        remote_path: str = None,
        is_screenshot: bool = None,
        is_download: bool = None,
    ) -> MythicFileRPCResponse:
        resp = await self.call(
            {
                "action": "register_file",
                "file": base64.b64encode(file).decode(),
                "delete_after_fetch": delete_after_fetch
                if delete_after_fetch is not None
                else True,
                "saved_file_name": saved_file_name
                if saved_file_name is not None
                else str(uuid.uuid4()),
                "task_id": self.task_id,
                "remote_path": remote_path if remote_path is not None else "",
                "is_screenshot": is_screenshot if is_screenshot is not None else False,
                "is_download": is_download if is_download is not None else False,
            }
        )
        return MythicFileRPCResponse(resp)

    async def get_file_by_name(self, filename: str) -> MythicFileRPCResponse:
        resp = await self.call(
            {
                "action": "get_file_by_name",
                "task_id": self.task_id,
                "filename": filename,
            }
        )
        return MythicFileRPCResponse(resp)

    async def remove_files_from_file_browser(self, files: list = []) -> MythicFileRPCResponse:
        # each entry in "files" is a dictionary with {"host": "hostname where file came from", "path", "full path to file that's removed"}
        #   naturally the path must match what's presented in the file browser or it won't match up
        resp = await self.call(
            {
                "action": "remove_files_from_file_browser",
                "task_id": self.task_id,
                "removed_files": files
            }
        )
        return MythicFileRPCResponse(resp)

    async def add_files_to_file_browser(self, files: dict = {}) -> MythicFileRPCResponse:
        # files should match the contents of the "file_browser" key in the docs https://docs.mythic-c2.net/customizing/hooking-features/file-browser#agent-file-browsing-responses
        resp = await self.call(
            {
                "action": "add_files_to_file_browser",
                "task_id": self.task_id,
                "file_browser": files
            }
        )
        return MythicFileRPCResponse(resp)

    async def call_c2_func(
        self, c2_profile: str, function_name: str, message: str
    ) -> MythicC2RPCResponse:
        resp = await self.call(
            {"action": function_name, "message": message, "task_id": self.task_id},
            c2_profile,
        )
        return MythicC2RPCResponse(resp)

    async def get_payload_by_uuid(self, uuid: str) -> MythicPayloadRPCResponse:
        resp = await self.call(
            {"action": "get_payload_by_uuid", "uuid": uuid, "task_id": self.task_id}
        )
        return MythicPayloadRPCResponse(resp)

    async def build_payload_from_template(
        self,
        uuid: str,
        destination_host: str = None,
        wrapped_payload: str = None,
        description: str = None,
    ) -> MythicPayloadRPCResponse:
        resp = await self.call(
            {
                "action": "build_payload_from_template",
                "uuid": uuid,
                "task_id": self.task_id,
                "destination_host": destination_host,
                "wrapped_payload": wrapped_payload,
                "description": description,
            }
        )
        return MythicPayloadRPCResponse(resp)

    async def build_payload_from_parameters(self,
                                            payload_type: str,
                                            c2_profiles: list,
                                            commands: list,
                                            build_parameters: list,
                                            filename: str = None,
                                            tag: str = None,
                                            destination_host: str = None,
                                            wrapped_payload: str = None) -> MythicPayloadRPCResponse:
        """
        :param payload_type: String value of a payload type name
        :param c2_profiles: List of c2 dictionaries of the form:
        { "c2_profile": "HTTP",
          "c2_profile_parameters": {
            "callback_host": "https://domain.com",
            "callback_interval": 20
          }
        }
        :param filename: String value of the name of the resulting payload
        :param tag: Description for the payload for the active callbacks page
        :param commands: List of string names for the commands that should be included
        :param build_parameters: List of build parameter dictionaries of the form:
        {
          "name": "version", "value": 4.0
        }
        :param destination_host: String name of the host where the payload will go
        :param wrapped_payload: If payload_type is a wrapper, wrapped payload UUID
        :return:
        """
        resp = await self.call(
            {
                "action": "build_payload_from_parameters",
                "task_id": self.task_id,
                "payload_type": payload_type,
                "c2_profiles": c2_profiles,
                "filename": filename,
                "tag": tag,
                "commands": commands,
                "build_parameters": build_parameters,
                "destination_host": destination_host,
                "wrapped_payload": wrapped_payload
            }
        )
        return MythicPayloadRPCResponse(resp)

    async def build_payload_from_MythicPayloadRPCResponse(self,
                                                          resp: MythicPayloadRPCResponse,
                                                          destination_host: str = None) -> MythicPayloadRPCResponse:
        c2_list = []
        for c2 in resp.c2info:
            c2_list.append({
                "c2_profile": c2["name"],
                "c2_profile_parameters": c2["parameters"]
            })
        resp = await self.call(
            {
                "action": "build_payload_from_parameters",
                "task_id": self.task_id,
                "payload_type": resp.payload_type,
                "c2_profiles": c2_list,
                "filename": resp.filename,
                "tag": resp.tag,
                "commands": resp.commands,
                "build_parameters": resp.build_parameters,
                "destination_host": destination_host,
                "wrapped_payload": resp.wrapped_payload
            }
        )
        return MythicPayloadRPCResponse(resp)

    async def register_payload_on_host(self,
                                       uuid: str,
                                       host: str):
        """
        Register a payload on a host for linking purposes
        :param uuid:
        :param host:
        :return:
        """
        resp = await self.call(
            {
                "action": "register_payload_on_host",
                "task_id": self.task_id,
                "uuid": uuid,
                "host": host
            }
        )
        return MythicPayloadRPCResponse(resp)

    async def user_output(self, user_output: str) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "user_output",
                "user_output": user_output,
                "task_id": self.task_id,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def update_callback(self, callback_info: dict) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "task_update_callback",
                "callback_info": callback_info,
                "task_id": self.task_id,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def register_artifact(
        self, artifact_instance: str, artifact_type: str, host: str = None
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "register_artifact",
                "task_id": self.task_id,
                "host": host,
                "artifact_instance": artifact_instance,
                "artifact": artifact_type,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def tokens_on_host(
        self, host: str = None, add: list = [], remove: list = []
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "rpc_tokens",
                "task_id": self.task_id,
                "host": host,
                "add": add,
                "remove": remove,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def logon_sessions_on_host(
        self, host: str = None, add: list = [], remove: list = []
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "rpc_logon_sessions",
                "task_id": self.task_id,
                "host": host,
                "add": add,
                "remove": remove,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def callback_tokens(
        self, host: str = None, add: list = [], remove: list = []
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "rpc_callback_tokens",
                "task_id": self.task_id,
                "host": host,
                "add": add,
                "remove": remove,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def authentication_packages_on_host(
        self, host: str = None, add: list = [], remove: list = []
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "rpc_authentication_packages",
                "task_id": self.task_id,
                "host": host,
                "add": add,
                "remove": remove,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def create_processes(
        self, host: str = None, add: list = [], remove: list = []
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "create_processes",
                "task_id": self.task_id,
                "host": host,
                "add": add,
                "remove": remove,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def get_running_job_contexts(
        self, host: str = None
    ) -> MythicResponseRPCResponse:
        resp = await self.call(
            {
                "action": "get_security_context_of_running_jobs_on_host",
                "task_id": self.task_id,
                "host": host,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def register_keystrokes(
        self, keystrokes: list = []
    ) -> MythicResponseRPCResponse:
        # keystrokes list entries are dictionaries with three components:
        #  "window_title", "user", and "keystrokes"
        #  window_title and user can be left out or blank and will be replaced with "UNKNOWN"
        #  however, "keystrokes" must always be present
        resp = await self.call(
            {
                "action": "register_keystrokes",
                "task_id": self.task_id,
                "keystrokes": keystrokes,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def register_credentials(
        self, credentials: list = []
    ) -> MythicResponseRPCResponse:
        # credentials list entries are dictionaries with the following components:
        #   "credential_type" - one of ["plaintext", "certificate", "hash", "key", "ticket", "cookie", "hex"]
        #   "realm" - the realm or domain for the credential
        #   "credential" - the value of the actual credential
        #   "account" - the user the account is for
        #   "comment" - any comment you want to specify about the credential as you save it
        
        resp = await self.call(
            {
                "action": "register_credentials",
                "task_id": self.task_id,
                "credentials": credentials,
            }
        )
        return MythicResponseRPCResponse(resp)

    async def search_database(self, table: str, search: dict) -> MythicResponseRPCResponse:
        # the search is a dictionary where the key is the element and the value is the regular expression for our match
        #   ex: {"name": ".*Slack.*"}
        resp = await self.call(
            {
                "action": "search_database",
                "task_id": self.task_id,
                "table": table,
                "search": search
            }
        )
        return MythicResponseRPCResponse(resp)


    async def start_socks(self, port: int) -> MythicSocksRPCResponse:
        resp = await self.call(
            {
                "action": "control_socks",
                "task_id": self.task_id,
                "start": True,
                "port": port,
            }
        )
        return MythicSocksRPCResponse(resp)

    async def stop_socks(self) -> MythicSocksRPCResponse:
        resp = await self.call(
            {
                "action": "control_socks",
                "stop": True,
                "task_id": self.task_id,
            }
        )
        return MythicSocksRPCResponse(resp)