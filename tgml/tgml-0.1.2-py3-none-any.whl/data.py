import base64
import os
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv


class TigerGraph:
    def __init__(self,
                 host: str = "http://localhost",
                 graph: str = None,
                 username: str = None,
                 password: str = None,
                 rest_port: str = "9000",
                 gs_port: str = "14240",
                 token_auth: bool = True) -> None:
        """Connection to the TigerGraph database. 

        Conceptually, this class represents the graph stored in the database. 
        Under the hood, it stores the necessary information to communicate with the TigerGraph database. 
        It can read `username` and `password` from environment variables `TGUSERNAME` and `TGPASSWORD`. 
        Hence, we recommend storing those credentials in the environment variables or 
        in a `.env` file instead of hardcoding them in code. However, if you do provide `username` 
        and `password` to this class constructor, the environment variables will be ignored.

        Args:
            host (str, optional): Address of the server. Defaults to "http://localhost".
            graph (str, optional): Name of the graph. Defaults to None.
            username (str, optional): Username. Defaults to None.
            password (str, optional): Password for the user. Defaults to None.
            rest_port (str, optional): Port for the REST endpoint. Defaults to "9000".
            gs_port (str, optional): Port for GraphStudio. Defaults to "14240".
            token_auth (bool, optional): Whether to use token authentication. Defaults to True.
        """
        self.graph_name = graph
        # Build endpoints
        self.host = host
        self._rest_port = rest_port
        self._gs_port = gs_port
        self._gsql_endpoint = "{}:{}/gsqlserver/gsql/file".format(
            host, gs_port)
        self._builtin_endpoint = "{}:{}/builtins/{}".format(
            host, rest_port, graph)
        self._query_endpoint = "{}:{}/query/{}".format(
            host, rest_port, graph)
        # Resolve credentials
        # If username or password is not provided, use environment variables.
        load_dotenv()
        if not username:
            username = os.getenv('TGUSERNAME')
        if not password:
            password = os.getenv("TGPASSWORD")
        # Set up request sessions
        # Rest API session that uses token to authenticate
        self._rest_session = requests.Session()
        if token_auth:
            resp = self._rest_session.get("{}:{}/requesttoken".format(host, rest_port),
                                          params={"graph": graph}, auth=(username, password))
            resp.raise_for_status()
            if resp.json()['error']:
                raise Exception(resp.json()['message'])
            self._rest_session.headers.update(
                {'Authorization': 'Bearer ' + resp.json()["results"]["token"]})
        else:
            user_pass = base64.b64encode('{}:{}'.format(
                username, password).encode()).decode()
            self._rest_session.headers.update(
                {'Authorization': "Basic {}".format(user_pass)})
        # GSQL session that uses passowrd to autheticate, as GSQL server does not support token.
        self._gsql_session = requests.Session()
        self._gsql_session.auth = (username, password)
        # Mixed session that uses both token and password.
        self._mixed_session = requests.Session()
        self._mixed_session.headers['Authorization'] = self._rest_session.headers['Authorization']
        self._mixed_session.headers['Basic-Auth'] = resp.request.headers['Authorization'] if token_auth else self._rest_session.headers['Authorization']
        # Instal misc queries on the graph
        resp = self._mixed_session.get(
            "{}:8000/misc/vertex_number/init".format(host), params={"graph": graph})
        resp.raise_for_status()

    def info(self) -> None:
        query = "USE GRAPH {}\nLS".format(self.graph_name)
        resp = self._gsql_session.post(self._gsql_endpoint,
                                       data=quote_plus(query.encode("utf-8")))
        resp.raise_for_status()
        for line in resp.text.splitlines():
            if not line.startswith("__GSQL__"):
                print(line)

    def number_of_vertices(self, vertex_type: str = None, filter_by: str = None) -> int:
        if not filter_by:
            payload = {"function": "stat_vertex_number"}
            if vertex_type:
                payload["type"] = vertex_type
            else:
                payload["type"] = "*"
            resp = self._rest_session.post(
                self._builtin_endpoint, json=payload)
            res_key = "count"
        else:
            payload = {"v_type": vertex_type, "filter_by": filter_by}
            resp = self._rest_session.get(
                self._query_endpoint+"/get_vertex_number", params=payload)
            res_key = "vertex_number"
        resp.raise_for_status()
        resp_json = resp.json()
        if vertex_type:
            return resp_json["results"][0][res_key]
        else:
            return sum(r[res_key] for r in resp_json["results"])

    def number_of_edges(self, edge_type: str = None) -> int:
        payload = {"function": "stat_edge_number"}
        if edge_type:
            payload["type"] = edge_type
        else:
            payload["type"] = "*"
        resp = self._rest_session.post(self._builtin_endpoint, json=payload)
        resp.raise_for_status()
        resp_json = resp.json()
        if edge_type:
            return resp_json["results"][0]["count"]
        else:
            return sum(r["count"] for r in resp_json["results"])
