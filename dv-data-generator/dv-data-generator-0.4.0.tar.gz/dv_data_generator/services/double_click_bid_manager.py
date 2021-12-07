from __future__ import annotations

import uuid
import requests

from dv_data_generator.helpers.file import write_csv
from dv_data_generator.helpers.dbm import get_report_url, try_run

from dv_data_generator.helpers.google_api import GoogleApi
from dv_data_generator.settings import HTTP_TIMEOUT


class DoubleClickBidManager(GoogleApi):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self._query_id = kwargs.get("query_id", None)
        self._report_url = None
        self._service = self.get_service("DBM")
        self._output_dir = kwargs.get("output_dir", "/tmp")
        self.num_retries = 0
        self.disposable = False if self._query_id else kwargs.get("disposable", False)
        self.recreate = kwargs.get("recreate", False)

    def set_num_retries(self, num_retries):
        self.num_retries = num_retries

    def __get_report(self, queryId: str) -> dict:
        return self._service.queries().getquery(queryId=queryId).execute(num_retries=self.num_retries)

    def __create_report(self, body: dict) -> dict:
        return self._service.queries().createquery(body=body).execute(num_retries=self.num_retries)

    def __run_report(self, queryId: str) -> dict:
        return self._service.queries().runquery(queryId=queryId, body={}).execute(num_retries=self.num_retries)

    def __delete_report(self, queryId: str) -> dict:
        try:
            return self._service.queries().deletequery(queryId=queryId).execute(num_retries=self.num_retries)
        except Exception:
            pass
    
    def __delete_report_if_disposable(self, queryId: str):
            if self.disposable:
                try_run(self.__delete_report, queryId)

    def __report_exists(self):
        try:
            self.__get_report(self._query_id)
        except Exception:
            return False
        return True

    def execute_query(self, query: dict) -> DoubleClickBidManager:
        """
        Runs a DBM API report query by creating the report, executing and deleting the report.
        To access the data, use the `data` property after running the query

        Args:
            query (dict): DBM Report Create Query
        """
        
        if self.recreate:
            self._query_id = None

        if not self.__report_exists() and self._query_id:
            raise Exception(f"Report {self._query_id} does not exist")

        if not self._query_id:
            assert "metadata" in query, "The query must have metadata"
            assert "format" in query["metadata"], "The query must have a format"
            assert query["metadata"]["format"] == "CSV", "The query type must be CSV"

            result = try_run(method=self.__create_report, value=query)
            
            assert "queryId" in result, "The report was not created"
            
            self._query_id = result["queryId"]

        unique_id = uuid.uuid4()
        file_location = f"{self._output_dir}/dv360_{self._query_id}_{unique_id}.csv"

        try_run(
            method=self.__run_report, value=self._query_id, fail_method=self.__delete_report_if_disposable
        )
        
        self._report_url = get_report_url(self._service, self._query_id)

        dataset = requests.get(self._report_url, timeout=HTTP_TIMEOUT)

        dataset.encoding = dataset.apparent_encoding
        csv_binary = dataset.text

        write_csv(file_location, csv_binary)

        self._file_location = file_location

        self.__delete_report_if_disposable(self._query_id)

        return self

    @property
    def data(self) -> dict:
        """A dataframe containing the report data

        Returns:
            DataFrame: Report data in a dataframe
        """
        return {
            "file_location": self._file_location,
            "query_id": self._query_id,
            "report_url": self._report_url
        }
