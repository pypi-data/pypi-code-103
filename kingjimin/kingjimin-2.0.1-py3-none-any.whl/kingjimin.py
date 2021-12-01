# please install multipledispatch 0.6.0
import requests
import contextlib
from urllib.parse import urljoin
import json
from multipledispatch import dispatch
import polling2
from .data import Model, Node, Benchmark, Task


class Error():
    def __init__(self, res = None, proc_msg = None):
        if res is not None:
            self.status_code = res.status_code
            self.df_msg = res.content
            print(f"[DeviceFarm Error] {self.df_msg}")
            print(f"[Status] {self.status_msg}")
        if proc_msg is not None:
            self.program_msg = proc_msg
            print(f"[Runtime Error] {self.program_msg}")
    
    @property
    def status_msg(self):
        # 4xx error -> client error, 5xx error -> server error
        if self.status_code == 400:
            return f"Bad Request({self.status_code})! Try again."
        elif self.status_code == 401:
            return f"Unauthorized({self.status_code})! Try again."
        elif self.status_code == 403:
            return f"Forbidden({self.status_code})! Try again."
        elif self.status_code == 404:
            return f"Not Found({self.status_code})! Try again."
        elif self.status_code == 500:
            return f"Internal Server Error({self.status_code})! Please contact to sanggeon.park@nota.ai"
        else:
            return f'Unknown Error. Original error message - {self. df_msg}'

class DeviceFarmGateway():
    def __init__(self, addr, port, network_request_time_out=5):
        self.address = f"http://{addr}:{port}/"
        self.timeout = network_request_time_out

    def _node_model_compatibility(self, model_uuid, node_uuid):
        node, error = self.get_node(node_uuid)
        model, error = self.get_model(model_uuid)
        if model.type not in node.available_model_types:
            return False
        else:
            return True

    def _check_status(self, res):
        if res.status_code >= 400: # More than 400 is seen as an issue on the device farm side.
            return False
        else:
            return True

    def _poll(self, add_str, method, files=None, params=None, headers=None):
        res = None
        try:
            if(method == "get"):
                res = polling2.poll(
                    lambda: requests.get(
                        url=urljoin(self.address, add_str),
                        files=files,
                        data=params,
                        headers=headers
                    ),
                    check_success = self._check_status,
                    step=5,
                    timeout=self.timeout)
            else:
                res = polling2.poll(
                    lambda: requests.post(
                        url=urljoin(self.address, add_str),
                        files=files,
                        data=params,
                        headers=headers
                    ),
                    check_success = self._check_status,
                    step=5,
                    timeout=self.timeout)
        except polling2.TimeoutException as e:
            return res, Error(e.last)
        return res, None

    def get_all_nodes(self):
        '''
        Devicefarm에 등록된 모든 노드 정보들을 가져온다.
        Return:
        성공: Node Instance들로 이루어진 list, None
        실패: None, Error
        '''
        res, error = self._poll(f"nodes", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        nodes = []
        [nodes.append(Node(res[i])) for i in range(0, len(res))]
        return nodes, None

    @dispatch(str)
    def get_node(self, node_uuid: str):
        '''
        node_uuid 값과 같은 uuid를 가진 노드 정보를 가져온다.
        node_uuid: 정보를 받아오고 싶은 노드의 uuid
        Return:
        성공: Node instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"nodes/{node_uuid}", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Node(res), None

    @dispatch(Node)
    def get_tasks_of_node(self, node: Node):
        return self.get_tasks_of_node(node.uuid)

    @dispatch(str)
    def get_tasks_of_node(self, node_uuid: str):
        '''
        node_uuid 값과 같은 uuid를 가진 노드의 task 정보들을 가져온다.
        node_uuid: Task 정보를 받아오고 싶은 노드의 uuid
        Return:
        성공: Task Instance들로 이루어진 list, None
        실패: None, Error
        '''
        res, error = self._poll(f"nodes/{node_uuid}/tasks", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        tasks = []
        [tasks.append(Task(res[i])) for i in range(0, len(res))]
        return tasks, None

    def get_task(self, task_uuid: str):
        '''
        task_uuid 값과 같은 uuid를 가진 Task 정보를 가져온다.
        task_uuid: 정보를 받아오고 싶은 Task의 uuid
        Return:
        성공: Task instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"tasks/{task_uuid}", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Task(res), None

    def get_all_models(self):
        '''
        Devicefarm에 등록된 모든 Model 정보들을 가져온다.
        Return:
        성공: Model Instance들로 이루어진 list, None
        실패: None, Error
        '''
        res, error = self._poll(f"models", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        models = []
        [models.append(Model(res[i])) for i in range(0, len(res))]
        return models, None

    def get_model(self, model_uuid: str):
        '''
        model_uuid 값과 같은 uuid를 가진 Model 정보를 가져온다.
        model_uuid: 정보를 받아오고 싶은 Model의 uuid
        Return:
        성공: Model instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Model(res), None

    @dispatch(Model)
    def get_available_nodes(self, model: Model):
        return self.get_available_nodes(model.uuid)

    @dispatch(str)
    def get_available_nodes(self, model_uuid: str):
        '''
        model_uuid에 해당하는 Model을 돌릴 수 있는 Node들을 가져온다.
        model_uuid: Benchmark를 돌리고 싶은 Model의 uuid
        Return:
        성공: Node Instance들로 이루어진 list, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/available_nodes", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        nodes = []
        [nodes.append(Node(res[i])) for i in range(0, len(res))]
        return nodes, None

    @dispatch(Model)
    def delete_model(self, model: Model):
        return self.delete_model(model.uuid)

    @dispatch(str)
    def delete_model(self, model_uuid: str):
        '''
        model_uuid에 해당하는 Model과 그 모델의 모든 Benchmark를 삭제하고, 삭제한 Model에 대한 Instance를 반환한다.
        model_uuid: 삭제할 Model의 uuid
        Return:
        성공: Model instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/delete", "post")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Model(res), None

    @dispatch(Model)
    def delete_only_model_file(self, model: Model):
        return self.delete_only_model_file(model.uuid)

    @dispatch(str)
    def delete_only_model_file(self, model_uuid: str):
        '''
        model_uuid에 해당하는 Model을 모델 파일만 삭제하고, 삭제한 Model에 대한 Instance를 반환한다.
        model_uuid: 삭제할 모델의 uuid
        Return:
        성공: Model instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/delete_model_file", "post")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Model(res), None       

    def upload_model(self, model_path: str, model_type: str):
        '''
        모델 파일을 업로드하고 Gateway에서 생성된 Model 정보를 돌려받는다.
        model_path: 업로드할 모델의 local path
        model_type: 업로드할 모델의 type (ex: onnx, onnx-trt, tflite)
        Return:
        성공: Gateway에서 생성된 Model Class instance, None
        실패: None, Error
        '''
        support_type = ['tflite', 'onnx', 'trt', 'onnx-trt']
        if model_type not in support_type:
            msg = f"Unsupported model type(received {model_type}). We can receive (list of str/list of Node/str/Node) types\n"
            return None, Error(proc_msg = msg)
        paths = {"model": model_path}
        params = {"type": model_type}
        with contextlib.ExitStack() as stack:
            files = {
                n: stack.enter_context(open(p, "rb")) for n, p in paths.items() if p
            }
            res, error = self._poll("upload_model", "post", files, params)
            if error is not None:
                return None, error
            res = json.loads(res.content.decode('utf-8'))
            return Model(res), None

    @dispatch(Model)
    def download_model_file(self, model: Model):
        return self.download_model_file(model.uuid)

    @dispatch(str)
    def download_model_file(self, model_uuid: str):
        '''
        model_uuid에 해당하는 Model의 파일을 다운로드한다.
        model_uuid: 다운받고 싶은 모델의 uuid
        Return:
        성공: byte 형태의 모델, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/download", "get")
        if error is not None:
            return None, error
        return res, None

    @dispatch(Model, list, dict)
    def start_benchmark(self, model: Model, node_list: list, benchmark_args: dict):
        return self.start_benchmark(model.uuid, node_list, benchmark_args)

    @dispatch(str, list, dict)
    def start_benchmark(self, model_uuid: str, node_list: list, benchmark_args: dict):
        '''
        benchmark_args에 있는 옵션과 함께 model_uuid에 해당하는 모델을 node_list에 있는 노드에서 벤치마크를 실행한다.
        model_uuid: 벤치마크를 돌릴 모델의 uuid
        node_list: 벤치마크를 돌릴 노드의 uuid(list)
        benchmark_args: 벤치마크 옵션(ex. use_gpu, use_xnnpack)
        Return:
        성공: Benchmark instance, Model Instance, Node Instance들로 이루어진 list, None
        실패: None, Error
        '''
        headers = {
            'Content-Type': 'application/json'
        }
        str_list_node = []
        for node in node_list:
            if type(node) is Node:
                if not self._node_model_compatibility(model_uuid, node.uuid):
                    msg = f"Can't run model on this node. Please check available nodes."
                    return None, Error(proc_msg = msg)
                else: 
                    str_list_node.append(node.uuid)
            elif type(node) is str:
                if not self._node_model_compatibility(model_uuid, node):
                    msg = f"Can't run model on this node. Please check available nodes."
                    return None, Error(proc_msg = msg)
                else: 
                    str_list_node.append(node)
            else:
                type_of_node = type(node)
                msg = f'Unsupported node type(received {type_of_node}). We can receive (list of str/list of Node) types'
                return None, Error(proc_msg = msg)

        benchmark_args["node_uuids"] = str_list_node
        print(benchmark_args)
        params = json.dumps(benchmark_args)
        res, error = self._poll(f"models/{model_uuid}/request_benchmark", "post", params=params, headers=headers)
        res = json.loads(res.content.decode('utf-8'))
        nodes = []
        [nodes.append(Node(res['nodes'][i])) for i in range(0, len(res['nodes']))]
        return Benchmark(res['benchmark']), Model(res['model']), nodes, error

    @dispatch(Model)
    def get_all_benchmarks_of_model(self, model: Model):
        return self.get_all_benchmarks_of_model(model.uuid)

    @dispatch(str)
    def get_all_benchmarks_of_model(self, model_uuid: str):
        '''
        model_uuid에 해당하는 Model의 벤치마크 정보들을 가져온다.
        model_uuid: Benchmark 정보들을 가져올 Model의 uuid
        Return:
        성공: Benchmark Instance들로 이루어진 list, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/benchmarks", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        benchmarks = []
        [benchmarks.append(Benchmark(res[i])) for i in range(0, len(res))]
        return benchmarks, None
    
    @dispatch(Model, str)
    def get_benchmark_of_model(self, model: Model, bench_uuid: str):
        return self.get_benchmark_of_model(model.uuid, bench_uuid)
        
    @dispatch(str, str)
    def get_benchmark_of_model(self, model_uuid: str, bench_uuid: str):
        '''
        model_uuid에 해당하는 Model에서 bench_uuid에 해당하는 벤치마크 정보를 가져온다.
        model_uuid: Benchmark 정보들을 가져올 Model의 uuid
        bench_uuid: 가져올 Benchmark의 uuid
        Return:
        성공: Benchmark, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/benchmarks/{bench_uuid}", "get")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Benchmark(res), None

    @dispatch(Benchmark)
    def delete_benchmark(self, bench: Benchmark):
        return self.delete_benchmark(bench.model_uuid, bench.uuid)

    @dispatch(Model, str)
    def delete_benchmark(self, model: Model, bench_uuid: str):
        return self.delete_benchmark(model.uuid, bench_uuid)

    @dispatch(str, str)
    def delete_benchmark(self, model_uuid: str, bench_uuid: str):
        '''
        model_uuid에 해당하는 Model에서 bench_uuid에 해당하는 벤치마크를 삭제한다.
        model_uuid: 삭제할 Benchmark가 등록된 Model의 uuid
        bench_uuid: 삭제할 Benchmark의 uuid
        Return:
        성공: 삭제한 Benchmark Instance, None
        실패: None, Error
        '''
        res, error = self._poll(f"models/{model_uuid}/benchmarks/{bench_uuid}/delete", "post")
        if error is not None:
            return None, error
        res = json.loads(res.content.decode('utf-8'))
        return Benchmark(res), None

    def wrapping_callback(self, callback_data):
        '''
        Benchmark status update될 때 받아온 callback_data를 Benchmark Instance로 반환한다.
        callback_data: Benchmark Instance로 변환할 callback data
        Return:
        성공: callback_data를 변환한 Benchmark Instance, None
        실패: None, Error
        '''
        try:
            callback_data = callback_data.decode('utf-8').replace("\'", "\"").replace("True", "true").replace("False", "false").replace("None", "null")
            callback_data = json.loads(callback_data)
        except:
            return None, Error(proc_msg='callback data is not valid.')
        return Benchmark(callback_data), None