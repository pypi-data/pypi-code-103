from .base import BaseCgi


class StatusJsonCgi(BaseCgi):
    def __init__(self, rest_client) -> None:
        super().__init__(rest_client)
        self.path = "statusjson.cgi"

    def host_count(self, **params) -> None:
        params = {"query": "hostcount", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def host_list(self, **params) -> None:
        params = {"query": "hostlist", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def host(self, host_name: str) -> None:
        params = {"query": "host", "hostname": host_name}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def service_count(self, **params) -> None:
        params = {"query": "servicecount", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def service_list(self, **params) -> None:
        params = {"query": "servicelist", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def service(self, host_name: str, description: str) -> None:
        params = {
            "query": "service",
            "hostname": host_name,
            "servicedescription": description,
        }
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def comment_count(self, **params) -> None:
        params = {"query": "commentcount", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def comment_list(self, **params) -> None:
        params = {"query": "commentlist", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def comment(self, id: int) -> None:
        params = {"query": "comment", "commentid": id}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def downtime_count(self, **params) -> None:
        params = {"query": "downtimecount", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def downtime_list(self, **params) -> None:
        params = {"query": "downtimelist", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def downtime(self, id: int) -> None:
        params = {"query": "downtime", "downtimeid": id}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def program_status(self, **params) -> None:
        params = {"query": "programstatus", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def performance_data(self, **params) -> None:
        params = {"query": "performancedata", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)

    def help(self, **params) -> None:
        params = {"query": "help", **params}
        response = self.rest_client.get(path=self.path, params=params)

        return self._result_handler(response)
