import os
import json
import logging
import io
import time
import threading
import tempfile
import shutil
import mlflow
import sys
from jupyter_client import KernelClient
from zmq.error import ZMQError

from ipykernel.ipkernel import IPythonKernel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(os.path.expanduser("~"), "mlflow_kernel.log")
log_file_handler = logging.FileHandler(filename=log_file, mode='w')
log_file_handler.setFormatter(
    logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(log_file_handler)

class MLFlowKernel(IPythonKernel):
    implementation = 'mlflow_kernel'
    implementation_version = 'generic'
    language = 'python'
    language_version = 'generic'
    language_info = {
        'name': 'python',
        'mimetype': 'text/x-python',
        'file_extension': '.py',
    }
    banner = "MLFlow Kernel - tracks every cell execution in MLFlow"

    def __init__(self, **kwargs):
        super(MLFlowKernel, self).__init__(**kwargs)
        self.connection_file = sys.argv[-1]
        if os.path.exists(self.connection_file):
            logger.info("connection file: " + self.connection_file)
        else:
            logger.error("Connection file "+self.connection_file+" not found")
            exit(-1)
        self.load_kernel_config()
        if self.mlflow_tracking_uri:
            self.load_mlflow_creds()
            try:
                mlflow.start_run()
                parent_run = mlflow.active_run()
            except Exception as ex:
                logger.error("Failed to start run: " + str(ex))
                exit(-1)
            self.parent_run_id = parent_run.info.run_id
            logger.info('parent run id = ' + str(self.parent_run_id))

    def load_kernel_config(self):
        config_file = os.path.join(os.path.expanduser("~"), ".jupyter", "mlflow_kernel_config.json")
        logger.info("config file: " + config_file)
        self.mlflow_tracking_uri = None
        self.debug_enabled = False
        if os.path.exists(config_file):
            with open(config_file) as cfp:
                conf_json = json.load(cfp)
            self.mlflow_tracking_uri = conf_json.get('mlflow_tracking_uri')
            logger.info("Tracking uri: "+str(self.mlflow_tracking_uri))
            if 'debug_enabled' in conf_json and conf_json['debug_enabled'].lower() == "true":
                self.debug_enabled = True

    def load_mlflow_creds(self):
        os.environ['MLFLOW_TRACKING_URI'] = self.mlflow_tracking_uri

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if self.mlflow_tracking_uri:
            self.load_mlflow_creds()
            try:
                with mlflow.start_run(nested=True) as cell_run:
                    run_id = mlflow.active_run().info.run_id
                    logger.info('run_id = ' + run_id)
                    result = self.do_execute_internal(
                        code, silent, store_history, user_expressions, allow_stdin)
            except Exception as ex:
                logger.error("Fatal: " + str(ex))
                exit(-1)
            return result
        else:
            result = super().do_execute(code, silent, store_history=store_history,
                                        user_expressions=user_expressions, allow_stdin=allow_stdin)
            return result

    def do_execute_internal(self, code, silent, store_history, user_expressions, allow_stdin):
        tmpdirbase = tempfile.mkdtemp()
        tmpdir = os.path.join(tmpdirbase, "cell_output")
        logger.info("tmpdir = " + tmpdir)
        os.mkdir(tmpdir)
        code_artifact_file = os.path.join(tmpdir, "code.txt")
        with open(code_artifact_file, "w") as cfp:
            cfp.write(code)
        stdouterr_artifact_file = os.path.join(tmpdir, "stdouterr.txt")
        data_artifact_file = os.path.join(tmpdir, "data")
        try:
            new_iopub_socket = self.get_new_iopub_socket()
        except Exception as ex:
            logger.error("Could not get new iopub_socket: " + str(ex))
            exit(-1)
        is_running = True
        iopub_reader = threading.Thread(
            target=capture_iopub_output,
            args=(new_iopub_socket, stdouterr_artifact_file, data_artifact_file, lambda: is_running))
        iopub_reader.start()
        result = super().do_execute(code, silent, store_history=store_history,
                                    user_expressions=user_expressions, allow_stdin=allow_stdin)
        ##Wait for 20ms to read all messages from socket
        iopub_reader.join(timeout=0.5)
        is_running = False
        ##Join again to cleanup the thread
        iopub_reader.join()
        new_iopub_socket.close()
        logger.info("Logging artifacts")
        try:
            mlflow.log_artifact(tmpdir)
        except Exception as ex:
            logger.info(str(ex))
        logger.info("Logging artifacts - completed")
        if not self.debug_enabled:
            shutil.rmtree(tmpdirbase)
        return result

    def do_shutdown(self, restart):
        if self.mlflow_tracking_uri:
            mlflow.end_run()
        return super().do_shutdown(restart)

    def get_new_iopub_socket(self):
        client = KernelClient()
        client.load_connection_file(connection_file=self.connection_file)
        return client.connect_iopub()


def capture_iopub_output(iopub_socket, stdouterr_artifact_file, data_artifact_file, is_running):
    data_text_fp = None
    stdfp = None
    data_text_artifact_file = data_artifact_file + "-text.txt"
    data_image_artifact_file = data_artifact_file + "-image-{0}.html"
    data_index = 1
    while is_running():
        try:
            msg = iopub_socket.recv(1)
            msg_str = msg.decode('utf-8')
            logger.info('msg received ## ' + msg_str)
            msg_json = json.loads(msg_str)
            if 'data' in msg_json:
                data_content = msg_json['data']
                ##Check for image content
                image_content = False
                for key, val in data_content.items():
                    if key.startswith('image/'):
                        image_content = True
                        break
                if image_content:
                    image_html_file = data_image_artifact_file.format(data_index)
                    data_index += 1
                    write_image_html(data_content, image_html_file)
                else:
                    if not data_text_fp:
                        data_text_fp = open(data_text_artifact_file, "w")
                    data_text_fp.write(str(msg_json))
            if 'name' in msg_json and msg_json['name'] == 'stdout':
                if not stdfp:
                    stdfp = open(stdouterr_artifact_file, "w")
                stdfp.write(msg_json['text'])
            if 'traceback' in msg_json:
                if not stdfp:
                    stdfp = open(stdouterr_artifact_file, "w")
                trace = msg_json['traceback']
                stdfp.write("\n".join(trace))
        except ZMQError as zqe:
            logger.debug('Error ZMQError: ' + str(zqe))
            time.sleep(0.02)
        except Exception as ex:
            logger.debug('Could not decode ' + str(msg_str))
    if stdfp:
        stdfp.close()
    if data_text_fp:
        data_text_fp.close()


def write_image_html(data_content, image_html_file):
    for key, val in data_content.items():
        if key.startswith('image/'):
            mime_type = key
            base64_content = val.rstrip('\n')
            break
    image_html = "<img src='data:{0};base64,{1}'/>".format(mime_type, base64_content)
    with open(image_html_file, "w") as imgfp:
        imgfp.write("<!DOCTYPE html>")
        imgfp.write("<html>")
        imgfp.write("<head><title>Display Image</title></head>")
        imgfp.write("<body><div>")
        imgfp.write(image_html)
        imgfp.write("</div></body>")
        imgfp.write("</html>")






