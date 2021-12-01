import json
import unittest
from mock import patch
from api_package.kingjimin.kingjimin import DeviceFarmGateway
from api_package.kingjimin.data import Node, Task, Benchmark, Model

def make_content(return_value, byte_str):
    response = return_value
    response.content = byte_str.encode('utf8')
    return response


class DFTests(unittest.TestCase):
    apiclass = DeviceFarmGateway("211.219.51.205", "8888")

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_all_nodes(self, mock_get):
        response = make_content(mock_get.return_value, """
            [{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-24 05:50:15.807822","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000",
            "ram":3795.0234375,"system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}]
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_all_nodes()
        self.assertEqual(type(res[0]), Node)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_node(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-24 05:50:15.807822","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000",
            "ram":3795.0234375,"system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_node('test')
        self.assertEqual(type(res), Node)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_tasks_of_node(self, mock_get):
        response = make_content(mock_get.return_value, """
            [{"additional_options":"","benchmark_uuid":"48a086e8-0df8-433c-912b-58f99fda65a6",
            "callback_url":"http://211.219.51.205:8888/callback","compilation_ended":null,
            "compilation_started":null,"converted_model_uuid":"","enable_op_profiling":true,
            "error":"Command './benchmark_model_armv6l --graph=711a7eaf-26df-4e38-94df-f638d82232f2/711a7eaf-26df-4e38-94df-f638d82232f2.model --use_xnnpack=true --use_gpu=true --num_threads=4 --enable_op_profiling=true --num_runs=25 --max_secs=180 --profiling_output_csv_file=711a7eaf-26df-4e38-94df-f638d82232f2/711a7eaf-26df-4e38-94df-f638d82232f2.model.info ' timed out after 180 seconds",
            "inference_result":null,"max_secs":180,
            "model_download_ended":"2021-11-15 06:32:49.479730","model_download_started":"2021-11-15 06:31:57.753750",
            "model_type":"tflite","model_url":"http://211.219.51.205:8888/models/a1ac5ef4-a5e2-4172-aa34-3e7fb3506fbc/download",
            "model_uuid":"a1ac5ef4-a5e2-4172-aa34-3e7fb3506fbc","node_uuid":"938b4106-3d3c-11ec-9388-b827eba9d011",
            "num_runs":25,"num_threads":4,"profile_result":null,"result_string":null,"status":"cancelled",
            "task_created":"2021-11-04 06:58:16.129073","task_ended":"2021-11-15 06:35:51.178799",
            "task_started":"2021-11-15 06:31:57.697456","use_gpu":true,"use_xnnpack":true,"uuid":"711a7eaf-26df-4e38-94df-f638d82232f2"}]
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_tasks_of_node('test')
        self.assertEqual(type(res[0]), Task)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_task(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"additional_options":"","benchmark_uuid":"48a086e8-0df8-433c-912b-58f99fda65a6",
            "callback_url":"http://211.219.51.205:8888/callback","compilation_ended":null,
            "compilation_started":null,"converted_model_uuid":"","enable_op_profiling":true,
            "error":"Command './benchmark_model_armv6l --graph=711a7eaf-26df-4e38-94df-f638d82232f2/711a7eaf-26df-4e38-94df-f638d82232f2.model --use_xnnpack=true --use_gpu=true --num_threads=4 --enable_op_profiling=true --num_runs=25 --max_secs=180 --profiling_output_csv_file=711a7eaf-26df-4e38-94df-f638d82232f2/711a7eaf-26df-4e38-94df-f638d82232f2.model.info ' timed out after 180 seconds",
            "inference_result":null,"max_secs":180,
            "model_download_ended":"2021-11-15 06:32:49.479730","model_download_started":"2021-11-15 06:31:57.753750",
            "model_type":"tflite","model_url":"http://211.219.51.205:8888/models/a1ac5ef4-a5e2-4172-aa34-3e7fb3506fbc/download",
            "model_uuid":"a1ac5ef4-a5e2-4172-aa34-3e7fb3506fbc","node_uuid":"938b4106-3d3c-11ec-9388-b827eba9d011",
            "num_runs":25,"num_threads":4,"profile_result":null,"result_string":null,"status":"cancelled",
            "task_created":"2021-11-04 06:58:16.129073","task_ended":"2021-11-15 06:35:51.178799",
            "task_started":"2021-11-15 06:31:57.697456","use_gpu":true,"use_xnnpack":true,"uuid":"711a7eaf-26df-4e38-94df-f638d82232f2"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_task('test')
        self.assertEqual(type(res), Task)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_all_models(self, mock_get):
        response = make_content(mock_get.return_value, """
            [{"available_nodes":[{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-24 08:53:21.678260","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,
            "system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"},
            {"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a53",
            "ipaddress":"192.168.1.86","last_connected":"2021-11-24 08:53:43.539924","machine":"aarch64",
            "name":"RaspberryPi3BPlus","port":"5000","processor":"","processor_speed":"1400000","ram":909.90234375,
            "system":"Linux","uuid":"41b3d1d2-0726-11ec-8a0b-b827eb9bee8e",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}],
            "benchmark_list_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/benchmarks",
            "created":"2021-11-18 04:42:33.484131",
            "download_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/download","has_file":true,
            "local_path":"./models/83637291-0413-4a4c-89dd-1c9d0cd3194f.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"83637291-0413-4a4c-89dd-1c9d0cd3194f"}]
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_all_models()
        self.assertEqual(type(res[0]), Model)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_model(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"available_nodes":[{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-24 08:53:21.678260","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,
            "system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"},
            {"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a53",
            "ipaddress":"192.168.1.86","last_connected":"2021-11-24 08:53:43.539924","machine":"aarch64",
            "name":"RaspberryPi3BPlus","port":"5000","processor":"","processor_speed":"1400000","ram":909.90234375,
            "system":"Linux","uuid":"41b3d1d2-0726-11ec-8a0b-b827eb9bee8e",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}],
            "benchmark_list_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/benchmarks",
            "created":"2021-11-18 04:42:33.484131",
            "download_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/download","has_file":true,
            "local_path":"./models/83637291-0413-4a4c-89dd-1c9d0cd3194f.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"83637291-0413-4a4c-89dd-1c9d0cd3194f"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_model('test')
        self.assertEqual(type(res), Model)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_available_nodes(self, mock_get):
        response = make_content(mock_get.return_value, """
            [{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-24 09:04:13.137108","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,
            "system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}]
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_available_nodes('test')
        self.assertEqual(type(res[0]), Node)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_delete_model(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"benchmark_list_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/benchmarks",
            "created":"2021-11-17 09:49:09.107975","download_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/download",
            "has_file":true,"local_path":"./models/09940e28-2a33-4a21-8ebf-6272a6b14cc5.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"09940e28-2a33-4a21-8ebf-6272a6b14cc5"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.delete_model('test')
        self.assertEqual(type(res), Model)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_delete_only_model_file(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"benchmark_list_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/benchmarks",
            "created":"2021-11-17 09:49:09.107975","download_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/download",
            "has_file":true,"local_path":"./models/09940e28-2a33-4a21-8ebf-6272a6b14cc5.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"09940e28-2a33-4a21-8ebf-6272a6b14cc5"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.delete_only_model_file('test')
        self.assertEqual(type(res), Model)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_upload_model(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"available_nodes":[{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-25 05:30:32.970691","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,
            "system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4",
            "version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}],
            "benchmark_list_uri":"/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/benchmarks",
            "created":"2021-11-25 05:33:05.936844","download_uri":"/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/download",
            "has_file":true,"local_path":"./models/c4af7556-24e4-4c51-8576-a3ff4b596ab7.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.upload_model('./fp16.tflite', 'tflite')
        self.assertEqual(type(res), Model)
        self.assertEqual(type(res.available_nodes[0]), Node)

    @patch.object(DeviceFarmGateway, "_node_model_compatibility", return_value=True)
    @patch.object(DeviceFarmGateway, "_poll")
    def test_start_benchmark(self, mock_get, mock_comp_get):
        response = make_content(mock_get.return_value, """
            {"benchmark":{"callback_url":"","created":"2021-11-25 05:52:22.166702",
            "model_uuid":"83637291-0413-4a4c-89dd-1c9d0cd3194f","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268",
            "uuid":"05f026bd-4ca5-4225-8982-95987c576ebd"},
            "model":{"benchmark_list_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/benchmarks",
            "created":"2021-11-18 04:42:33.484131","download_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/download",
            "has_file":true,"local_path":"./models/83637291-0413-4a4c-89dd-1c9d0cd3194f.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/83637291-0413-4a4c-89dd-1c9d0cd3194f/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"83637291-0413-4a4c-89dd-1c9d0cd3194f"},
            "nodes":[{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72",
            "ipaddress":"192.168.1.88","last_connected":"2021-11-25 05:51:42.711353","machine":"aarch64",
            "name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,
            "system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"}]}
        """)
        mock_get.return_value = response, None
        mock_comp_get.return_value = True
        bench, model, nodes, err = DFTests.apiclass.start_benchmark('test', ['test'], {'test':'test'})
        self.assertEqual(type(bench), Benchmark)
        self.assertEqual(type(model), Model)
        self.assertEqual(type(nodes[0]), Node)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_all_benchmarks_of_model(self, mock_get):
        response = mock_get.return_value
        byte_str = """[{"callback_url":"","cancelled_task_count":0,"compiling_task_count":0,"created":"2021-11-25 06:44:29.548935","downloading_task_count":0,"ended_task_count":1,"model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","running_task_count":0,"task_node_pairs":[{"node":{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72","ipaddress":"192.168.1.88","last_connected":"2021-11-25 06:44:36.378476","machine":"aarch64","name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,"system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"},"task":{"additional_options":"--allow_fp16","benchmark_uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","callback_url":"http://211.219.51.205:8888/callback","compilation_ended":null,"compilation_started":null,"converted_model_uuid":"","enable_op_profiling":false,"error":null,"inference_result":{"inference_timings":{"first inference":140706.0,"inference (avg)":74481.6,"init":18738.0,"warmup (avg)":85791.2},"memory_footprints":{"init":6.44141,"overall":64.8633}},"max_secs":180,"model_download_ended":"2021-11-25 06:44:48.641992","model_download_started":"2021-11-25 06:44:47.988385","model_type":"tflite","model_url":"http://211.219.51.205:8888/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/download","model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","node_uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","num_runs":50,"num_threads":4,"profile_result":null,"result_string":"STARTING!\nUnconsumed cmdline flags: --allow_fp16\nLog parameter values verbosely: [0]\nMin num runs: [50]\nMax runs duration (seconds): [180]\nNum threads: [4]\nGraph: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model]\nEnable op profiling: [0]\nCSV File to export profiling data to: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model.info]\n#threads used for CPU inference: [4]\nUse gpu: [1]\nUse xnnpack: [1]\nLoaded model b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model\nThe GPU delegate compile options are only supported on Android or iOS platforms or when the tool was built with -DCL_DELEGATE_NO_GL.\nGPU acceleration is unsupported on this platform.\nXNNPACK delegate created.\nGoing to apply 1 delegates one after another.\nExplicitly applied XNNPACK delegate, and the model graph will be partially executed by the delegate w/ 22 delegate kernels.\nThe input model file size (MB): 0.541472\nInitialized session in 18.738ms.\nRunning benchmark for at least 1 iterations and at least 0.5 seconds but terminate if exceeding 180 seconds.\ncount=6 first=140706 curr=74599 min=74599 max=140706 avg=85791.2 std=24559\n\nRunning benchmark for at least 50 iterations and at least 1 seconds but terminate if exceeding 180 seconds.\ncount=50 first=74456 curr=74516 min=73909 max=75323 avg=74481.6 std=268\n\nInference timings in us: Init: 18738, First inference: 140706, Warmup (avg): 85791.2, Inference (avg): 74481.6\nNote: as the benchmark tool itself affects memory footprint, the following is only APPROXIMATE to the actual memory footprint of the model at runtime. Take the information at your discretion.\nPeak memory footprint (MB): init=6.44141 overall=64.8633\n","status":"ended","task_created":"2021-10-07 10:27:48.277490","task_ended":"2021-11-25 06:44:53.496368","task_started":"2021-11-25 06:44:47.611427","use_gpu":true,"use_xnnpack":true,"uuid":"b40647a5-6c5b-48ad-b196-745488334183"}}],"user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","waiting_task_count":0}]"""
        response.content = byte_str.replace('\n', '\\n').encode('utf-8')
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_all_benchmarks_of_model('test')
        self.assertEqual(type(res[0]), Benchmark)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_get_benchmark_of_model(self, mock_get):
        response = mock_get.return_value
        byte_str = """{"callback_url":"","cancelled_task_count":0,"compiling_task_count":0,"created":"2021-11-25 06:44:29.548935","downloading_task_count":0,"ended_task_count":1,"model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","running_task_count":0,"task_node_pairs":[{"node":{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72","ipaddress":"192.168.1.88","last_connected":"2021-11-25 06:44:36.378476","machine":"aarch64","name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,"system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"},"task":{"additional_options":"--allow_fp16","benchmark_uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","callback_url":"http://211.219.51.205:8888/callback","compilation_ended":null,"compilation_started":null,"converted_model_uuid":"","enable_op_profiling":false,"error":null,"inference_result":{"inference_timings":{"first inference":140706.0,"inference (avg)":74481.6,"init":18738.0,"warmup (avg)":85791.2},"memory_footprints":{"init":6.44141,"overall":64.8633}},"max_secs":180,"model_download_ended":"2021-11-25 06:44:48.641992","model_download_started":"2021-11-25 06:44:47.988385","model_type":"tflite","model_url":"http://211.219.51.205:8888/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/download","model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","node_uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","num_runs":50,"num_threads":4,"profile_result":null,"result_string":"STARTING!\nUnconsumed cmdline flags: --allow_fp16\nLog parameter values verbosely: [0]\nMin num runs: [50]\nMax runs duration (seconds): [180]\nNum threads: [4]\nGraph: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model]\nEnable op profiling: [0]\nCSV File to export profiling data to: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model.info]\n#threads used for CPU inference: [4]\nUse gpu: [1]\nUse xnnpack: [1]\nLoaded model b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model\nThe GPU delegate compile options are only supported on Android or iOS platforms or when the tool was built with -DCL_DELEGATE_NO_GL.\nGPU acceleration is unsupported on this platform.\nXNNPACK delegate created.\nGoing to apply 1 delegates one after another.\nExplicitly applied XNNPACK delegate, and the model graph will be partially executed by the delegate w/ 22 delegate kernels.\nThe input model file size (MB): 0.541472\nInitialized session in 18.738ms.\nRunning benchmark for at least 1 iterations and at least 0.5 seconds but terminate if exceeding 180 seconds.\ncount=6 first=140706 curr=74599 min=74599 max=140706 avg=85791.2 std=24559\n\nRunning benchmark for at least 50 iterations and at least 1 seconds but terminate if exceeding 180 seconds.\ncount=50 first=74456 curr=74516 min=73909 max=75323 avg=74481.6 std=268\n\nInference timings in us: Init: 18738, First inference: 140706, Warmup (avg): 85791.2, Inference (avg): 74481.6\nNote: as the benchmark tool itself affects memory footprint, the following is only APPROXIMATE to the actual memory footprint of the model at runtime. Take the information at your discretion.\nPeak memory footprint (MB): init=6.44141 overall=64.8633\n","status":"ended","task_created":"2021-10-07 10:27:48.277490","task_ended":"2021-11-25 06:44:53.496368","task_started":"2021-11-25 06:44:47.611427","use_gpu":true,"use_xnnpack":true,"uuid":"b40647a5-6c5b-48ad-b196-745488334183"}}],"user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","waiting_task_count":0}"""
        response.content = byte_str.replace('\n', '\\n').encode('utf-8')
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.get_benchmark_of_model('test', 'test')
        self.assertEqual(type(res), Benchmark)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_delete_only_model_file(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"benchmark_list_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/benchmarks",
            "created":"2021-11-17 09:49:09.107975","download_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/download",
            "has_file":true,"local_path":"./models/09940e28-2a33-4a21-8ebf-6272a6b14cc5.tflite","name":"fp16.tflite",
            "size":541472,"start_benchmark_uri":"/models/09940e28-2a33-4a21-8ebf-6272a6b14cc5/request_benchmark",
            "type":"tflite","user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"09940e28-2a33-4a21-8ebf-6272a6b14cc5"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.delete_only_model_file('test')
        self.assertEqual(type(res.type), str)

    @patch.object(DeviceFarmGateway, "_poll")
    def test_delete_benchmark(self, mock_get):
        response = make_content(mock_get.return_value, """
            {"callback_url":"","created":"2021-11-25 06:44:29.548935","model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7",
            "user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3"}
        """)
        mock_get.return_value = response, None
        res, err = DFTests.apiclass.delete_benchmark('test', 'test')
        self.assertEqual(type(res), Benchmark)

    def test_wrapping_callback(self):
        byte_str = """{'uuid':'cd95cc53-149a-4f60-b006-bd8e18d063a0','model_uuid':'f380b34b-8e5c-454f-b57f-d20cc73257c6',
        'created':'2021-11-10 07:57:11.532532','user_id':'2BE9A298-EB22-42C9-BFED-485D72B02268',
        'callback_url':'http://192.168.1.202:8000/hi/','task_node_pairs':[{'node':{'uuid':'ac612d5e-072b-11ec-90dc-00044be5a3c1',
        'name':'Jetson-Nano','available_model_types':'trt, tflite, onnx, onnx-trt','machine':'aarch64','cpu_info':'arm,cortex-a57-64bit',
        'processor':'aarch64','processor_speed':'1479000','system':'Linux','version':'#1 SMP PREEMPT Mon Jul 26 12:13:06 PDT 2021',
        'ram':3964.1015625,'ipaddress':'192.168.1.164','port':'5000','active':True,'last_connected':'2021-11-10 07:57:12.036175'},
        'task':{'uuid':'584bc4a7-042e-44d0-be83-f735309c6585','node_uuid':'ac612d5e-072b-11ec-90dc-00044be5a3c1',
        'model_uuid':'f380b34b-8e5c-454f-b57f-d20cc73257c6','benchmark_uuid':'cd95cc53-149a-4f60-b006-bd8e18d063a0','status':'downloading',
        'model_type':'tflite','task_created':'2021-10-26 12:37:57.814000','task_started':'2021-11-10 07:57:21.488314','task_ended':None,
        'model_download_started':'2021-11-10 07:57:21.504452','model_download_ended':None,'compilation_started':None,'compilation_ended':None,
        'model_url':'http://211.219.51.205:8888/models/f380b34b-8e5c-454f-b57f-d20cc73257c6/download','callback_url':'http://211.219.51.205:8888/callback',
        'converted_model_uuid':'','use_xnnpack':True,'use_gpu':True,'enable_op_profiling':False,'num_threads':4,'num_runs':50,'max_secs':180,
        'result_string':None,'profile_result':None,'inference_result':None,'error':None,'additional_options':'--allow_fp16'}}],
        'waiting_task_count':0,'downloading_task_count':1,'compiling_task_count':0,'running_task_count':0,'ended_task_count':0,'cancelled_task_cout':0}"""
        res, err = DFTests.apiclass.wrapping_callback(byte_str.encode('utf-8'))
        self.assertEqual(type(res), Benchmark)

class DFGatewayTests(unittest.TestCase):
    apiclass = DeviceFarmGateway("211.219.51.205", "8888")
    model_uuid = None

    def test_gateway_1_connect(self):
        # gateway가 잘 연결되는지 테스트합니다.
        res, err = self.apiclass._poll(f"", "get")
        self.assertEqual(res.status_code, 200)

        # _poll()이 잘못된 주소를 받으면 404 에러를 잘 뱉는지 테스트합니다.
        res, err = self.apiclass._poll("invalid", "get")
        self.assertEqual(err.status_code, 404)

        # _poll()이 잘못된 메소드(post, get)을 받으면 405 에러를 잘 뱉는지 테스트합니다.
        res, err = self.apiclass._poll(f"", "post")
        self.assertEqual(err.status_code, 405)

    def test_gateway_2_get_all_nodes(self):
        # get_all_nodes()가 잘 동작하는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.get_all_nodes()
        self.assertEqual(type(res[0]), Node)

    def test_gateway_3_get_node(self):
        # get_node()가 주어진 uuid의 노드를 잘 가져오는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.get_node('8fefe378-ff5a-11eb-9305-dca6328392f4')
        self.assertEqual(type(res), Node)

        # get_node()가 잘못된 node uuid를 받았을 때 에러를 잘 뱉는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.get_node('invalid_value')
        self.assertIsNotNone(err)

    def test_gateway_4_get_tasks_of_node(self):
        # get_tasks_of_node()가 주어진 uuid의 노드에서 Task들을 잘 가져오는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.get_tasks_of_node('8fefe378-ff5a-11eb-9305-dca6328392f4')
        self.assertEqual(type(res[0]), Task)

        # get_tasks_of_node()가 잘못된 node uuid를 받았을 때 에러를 잘 뱉는지 테스트합니다.
        # -> 404 에러가 아니라 공백의 값이 return 됨. 현재 수정 중.
        # res, err = DFGatewayTests.apiclass.get_tasks_of_node('invalid_value')
        # self.assertIsNotNone(err)

    def test_gateway_5_upload_model(self):
        # upload_model()이 주어진 모델 파일을 잘 업로드하는지 테스트합니다.
        res, err = DFTests.apiclass.upload_model('./fp16.tflite', 'tflite')
        self.assertEqual(type(res), Model)
        self.assertEqual(type(res.available_nodes[0]), Node)
        self.model_uuid = res.uuid

        # upload_model()이 주어진 모델 파일과 다른 타입을 입력받았을 때 에러를 잘 뱉는지 테스트합니다.
        # -> 확장자 체크는 하지 않기로 함
        # res, err = DFGatewayTests.apiclass.upload_model('./fp16.tflite', 'onnx')

        # upload_model()이 지원하지 않는 타입을 입력받았을 때 에러를 잘 뱉는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.upload_model('./fp16.tflite', 'a')
        self.assertIsNotNone(err)

        # upload_model()이 유효하지 않은 파일 경로를 입력받았을 때 에러를 잘 뱉는지 테스트합니다.
        # -> 프로그램 종료가 뜸
        # res, err = DFGatewayTests.apiclass.upload_model('./invalid_value.tflite', 'tflite')
        # self.assertIsNotNone(err)

        # upload_model()이 지원하지 않는 타입의 모델 파일을 입력받았을 때 에러를 잘 뱉는지 테스트합니다.
        # -> 에러를 뱉지 않고 업로드됨
        # res, err = DFGatewayTests.apiclass.upload_model('./test_model.h5', 'tflite')
        # self.assertIsNotNone(err)

        # upload_model()이 아무 내용이 없는 모델 파일을 입력받았을 때 에러를 잘 뱉는지 테스트합니다.
        # -> 에러를 뱉지 않고 업로드됨
        # res, err = DFGatewayTests.apiclass.upload_model('./test_model.tflite', 'tflite')
        # self.assertIsNotNone(err)

    def test_gateway_6_get_all_models(self):
        # get_all_models()가 잘 동작하는지 테스트합니다.
        res, err = DFGatewayTests.apiclass.get_all_models()
        self.assertEqual(type(res[0]), Model)

    def test_gateway_7_to_json(self):
        # to_json()이 올바른 dict string을 받았을 때 json 형태로 변환을 잘 하는지 테스트합니다.
        byte_str = """{"callback_url":"","cancelled_task_count":0,"compiling_task_count":0,"created":"2021-11-25 06:44:29.548935","downloading_task_count":0,"ended_task_count":1,"model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","running_task_count":0,"task_node_pairs":[{"node":{"active":true,"available_model_types":"tflite, onnx","cpu_info":"arm,cortex-a72","ipaddress":"192.168.1.88","last_connected":"2021-11-25 06:44:36.378476","machine":"aarch64","name":"RaspberryPi4","port":"5000","processor":"","processor_speed":"1500000","ram":3795.0234375,"system":"Linux","uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","version":"#1441 SMP PREEMPT Tue Aug 3 18:14:03 BST 2021"},"task":{"additional_options":"--allow_fp16","benchmark_uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","callback_url":"http://211.219.51.205:8888/callback","compilation_ended":null,"compilation_started":null,"converted_model_uuid":"","enable_op_profiling":false,"error":null,"inference_result":{"inference_timings":{"first inference":140706.0,"inference (avg)":74481.6,"init":18738.0,"warmup (avg)":85791.2},"memory_footprints":{"init":6.44141,"overall":64.8633}},"max_secs":180,"model_download_ended":"2021-11-25 06:44:48.641992","model_download_started":"2021-11-25 06:44:47.988385","model_type":"tflite","model_url":"http://211.219.51.205:8888/models/c4af7556-24e4-4c51-8576-a3ff4b596ab7/download","model_uuid":"c4af7556-24e4-4c51-8576-a3ff4b596ab7","node_uuid":"8fefe378-ff5a-11eb-9305-dca6328392f4","num_runs":50,"num_threads":4,"profile_result":null,"result_string":"STARTING!\nUnconsumed cmdline flags: --allow_fp16\nLog parameter values verbosely: [0]\nMin num runs: [50]\nMax runs duration (seconds): [180]\nNum threads: [4]\nGraph: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model]\nEnable op profiling: [0]\nCSV File to export profiling data to: [b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model.info]\n#threads used for CPU inference: [4]\nUse gpu: [1]\nUse xnnpack: [1]\nLoaded model b40647a5-6c5b-48ad-b196-745488334183/b40647a5-6c5b-48ad-b196-745488334183.model\nThe GPU delegate compile options are only supported on Android or iOS platforms or when the tool was built with -DCL_DELEGATE_NO_GL.\nGPU acceleration is unsupported on this platform.\nXNNPACK delegate created.\nGoing to apply 1 delegates one after another.\nExplicitly applied XNNPACK delegate, and the model graph will be partially executed by the delegate w/ 22 delegate kernels.\nThe input model file size (MB): 0.541472\nInitialized session in 18.738ms.\nRunning benchmark for at least 1 iterations and at least 0.5 seconds but terminate if exceeding 180 seconds.\ncount=6 first=140706 curr=74599 min=74599 max=140706 avg=85791.2 std=24559\n\nRunning benchmark for at least 50 iterations and at least 1 seconds but terminate if exceeding 180 seconds.\ncount=50 first=74456 curr=74516 min=73909 max=75323 avg=74481.6 std=268\n\nInference timings in us: Init: 18738, First inference: 140706, Warmup (avg): 85791.2, Inference (avg): 74481.6\nNote: as the benchmark tool itself affects memory footprint, the following is only APPROXIMATE to the actual memory footprint of the model at runtime. Take the information at your discretion.\nPeak memory footprint (MB): init=6.44141 overall=64.8633\n","status":"ended","task_created":"2021-10-07 10:27:48.277490","task_ended":"2021-11-25 06:44:53.496368","task_started":"2021-11-25 06:44:47.611427","use_gpu":true,"use_xnnpack":true,"uuid":"b40647a5-6c5b-48ad-b196-745488334183"}}],"user_id":"2BE9A298-EB22-42C9-BFED-485D72B02268","uuid":"b9032629-c7ab-4904-8bab-4019cf225ae3","waiting_task_count":0}"""
        byte_str = byte_str.replace('\n', '\\n').encode('utf-8')
        bench = Benchmark(json.loads(byte_str))
        bench = bench.to_json()
        self.assertEqual(type(json.loads(bench)), dict)