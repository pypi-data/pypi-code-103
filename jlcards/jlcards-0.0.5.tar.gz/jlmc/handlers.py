import os, subprocess
import json
import re
from pathlib import Path

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join

import tornado
from tornado.web import StaticFileHandler

def get_common_root_folder(path_one, path_two):
    path_onel = path_one.split('/')
    path_twol = path_one.split('/')
    root_path = ''
    for i, c in enumerate(path_one):
        if path_two[i] == c:
            root_path += c
        else:
            break
    if not root_path:
        raise Exception("No common file system found. Unable to find the notebook.")
    else:
        return root_path

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"data": "This is /jlcards/hello endpoint!"}))

    @tornado.web.authenticated
    def post(self):
        # input_data is a dictionary with a key "path"
        input_data = self.get_json_body()
        notebook_file_path = Path(input_data['path']).resolve()
        code_file_path = Path(__file__).resolve()
        data = {}
        if input_data["path"].endswith(".ipynb"):
            try:
                result = subprocess.run(["node", f"{os.path.dirname(code_file_path)}/model_card_source/main.js", 
                    notebook_file_path], capture_output=True, text=True)
                data = json.loads(result.stdout)
            except Exception as e:
                data["msg"] = f"Internal server error: {e}" 
        self.finish(json.dumps(data))


def setup_handlers(web_app, url_path):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # Prepend the base_url so that it works in a JupyterHub setting
    route_pattern = url_path_join(base_url, url_path, "hello")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Prepend the base_url so that it works in a JupyterHub setting
    doc_url = url_path_join(base_url, url_path, "public")
    doc_dir = os.getenv(
        "JLAB_SERVER_EXAMPLE_STATIC_DIR",
        os.path.join(os.path.dirname(__file__), "public"),
    )
    handlers = [("{}/(.*)".format(doc_url), StaticFileHandler, {"path": doc_dir})]
    web_app.add_handlers(".*$", handlers)
