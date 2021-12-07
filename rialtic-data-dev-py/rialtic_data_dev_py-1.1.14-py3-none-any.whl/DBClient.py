import datetime
import json
import os
import requests
from typing import Optional, List, Dict
from dataUtils.APIErrors import ReadAPIErrorFromHTTPResponse

from dataUtils.decor import retry
from fhir.resources.claim import Claim, ClaimItem
from fhir.resources.period import Period
from schema.insight_engine_request import HistoryClaim


class DBClient:
    @staticmethod
    # https://www.python.org/dev/peps/pep-0484/#the-problem-of-forward-declarations
    def GetDBClient(apiKey: str) -> 'DBClient':
        return DBClient(apiKey)

    def __init__(self, apiKey: str):
        self._apiKey = apiKey
        self._devAPI = "https://ommunitystaging-enginedevapi.dev.rialtic.dev/"
        self._headers = {
            "Content-Type": "application/json",
            "x-api-key": self._apiKey
        }
        self._defenses : Dict[str,dict] = {}

    def init_defenses(self, transaction_id: str, engine_id: str, **kwargs) -> Dict[str, dict]:
        defenses: List = self.GetAllDefense(transaction_id, engine_id, **kwargs) or list()
        self._defenses = {defense['node']: defense for defense in defenses}
        return self._defenses

    def get_defense_by_node(self, node: str) -> (str, str):
        row = self._defenses.get(
            node,
            {'excerpt':'', 'uuid':''} # default
        )
        return row["excerpt"], row["uuid"].replace('"', '').strip()

    def get_defense_by_subcode(self, transactionid: str, subcode: str) -> (str, str, str):
        query = f"SELECT string_agg(excerpt, ' ')  FROM demodb.defense WHERE subcode='{subcode}'"
        data, err = self.GetReferenceData(transactionid, query)
        if err is not None:
            return None, None, err
        elif data[0]["string_agg"] is None:
            return "", "", None
        else:
            return data[0]["string_agg"], subcode, None


    def GetDefense(self, transactionid: str, uuid: str, subcode: str, node: str) -> (str, str, str):
        if subcode.strip() == "":
            query = f"SELECT excerpt, defenseuuid FROM demodb.defense WHERE uuid='{uuid}' AND nodename='{node}'"
        else:
            query = f'''
            SELECT excerpt, defenseuuid 
            FROM demodb.defense 
            WHERE uuid='{uuid}' AND subcode='{node}' AND nodename='{node}'
            '''

        data, err = self.GetReferenceData(transactionid, query)

        if err is not None:
            return None, None, err
        elif data is None:
            return "Not found", "", None
        else:
            return data[0]["excerpt"], data[0]["defenseuuid"].replace('"', '').strip(), None

    def GetAllDefense(self, transactionid: str, uuid: str, **kwargs) -> Optional[List[Dict[str, str]]]:
        subcode = kwargs.get("subcode", None)

        if subcode is None:
            query = f"SELECT excerpt, defenseuuid, nodename FROM demodb.defense WHERE uuid='{uuid}'"
        else:
            query = f"SELECT excerpt, defenseuuid, nodename FROM demodb.defense WHERE uuid='{uuid}' AND subcode='{subcode}'"

        data, err = self.GetReferenceData(transactionid, query)

        if err is not None:
            return None
        elif data is None:
            return None
        else:
            return [{'node': d["nodename"], 'excerpt': d["excerpt"], 'uuid': d["defenseuuid"].replace('"', '').strip()} for d in data]


    @retry
    def GetHistory(
            self,
            transactionId: str,
            start_date: datetime.date,
            end_date: datetime.date
    ) -> (list, str):
        if os.environ.get('RIALTIC_DATA_ENV') == 'local':
            return self._getHistoryLocal(os.environ.get('RIALTIC_HISTORY_FILE'), transactionId, start_date, end_date)
        else:
            return self._getHistoryDev(transactionId, start_date, end_date)

    @retry
    def GetReferenceData(self, transactionId: str, query: str) -> (list, str):
        return self._getReferenceDataDev(transactionId, query)

    def _getHistoryDev(self, transactionId: str, start_date: datetime.date, end_date: datetime.date) -> (list, str):
        historyEvent = {
            'transactionId': transactionId,
            'start_date': start_date,
            'end_date': end_date
        }
        res = requests.post(self._devAPI + "history", json=historyEvent, headers=self._headers)

        if res.ok:
            return res.json(), None
        else:
            try:
                return None, res.json()["Message"]
            except KeyError:
                return None, res.json()["message"]

    def _getHistoryLocal(self, filename: str, transactionId: str, start_date: datetime.date, end_date: datetime.date) -> (list, str):
        with open(os.path.join(os.getcwd(), filename), 'r') as history_file:
            history_list = json.loads(history_file.read())
            history = []
            for hc in history_list:
                history_claim = HistoryClaim.parse_obj(hc)
                if history_claim.transaction_id == transactionId:
                    claim = Claim.parse_obj(history_claim.claim)
                    billable_period = Period.parse_obj(claim.billablePeriod)
                    period_start = billable_period.start
                    period_end = billable_period.end
                    if start_date <= period_end and end_date >= period_start:
                        history.append(claim)

            return history, None

    def _getReferenceDataDev(self, transactionId: str, query: str) -> (list, str):
        referenceDataEvent = {
            'transactionId': transactionId,
            'query': query,
        }

        res = requests.post(self._devAPI + "referencedata", json=referenceDataEvent, headers=self._headers)

        # LOGGER.info("%s", vars(res))
        if res.ok:
            return res.json(), None
        else:
            try:
                return None, str(ReadAPIErrorFromHTTPResponse(res))
            except KeyError:
                return None, res.json()["message"]
