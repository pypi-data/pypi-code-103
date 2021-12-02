from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class SerasaData(BaseData):
    """Serasa Data.

    Contains all data prospect from Tst Data Source.

    Default Properties
    ==================
    * tax_id (str):                     The TaxId prospected.
                                        must be a valid CNPJ, formatted or not.
    * integration_status (str):         The current Integration Status, please check the
                                        `find_current_status` method for more info.
    * status_reason (str):              The human friendly reason for current status
    * prospect_date (datetime):         The prospect datetime.
    * payload (dict):                   Original payload received from prospection.
    * timeit                            Time in seconds for retrieving data.
    * datasource_base_url               Data Source Base Url

    Serasa Properties
    ====================
    * request_params (str):             Request Data send to Serasa.
                                        Serasa response is available in `payload` field
    * request_datetime (datatime):      Serasa processing DateTime (NOT WORKING)
    * total_records (int):              Total records in Serasa Response (NOT WORKING)
    * has_negative_annotations (bool):  TaxId has any negative annotations (NOT WORKING)
    * data (Dict):                      All Serasa info parsed from Serasa response


    Serasa Data Dictionary
    ====================
    Each Serasa Function response are parsed and stored
    in `data` field, into your respective key:

    Please make note, at this time, this prospect is a Working-In-Progress and
    none of this info are validated yet.

    USE THIS INFORMATION WITH CAUTION.

    * bad_checks - Returns info about Serasa's Bad Checks (Serasa function N270)
    * serasa_score - Returns Serasa's Score info (F900)
    * protest - Returns Serasa's Protest info (N250)
    * financial_pending - Returns Serasa's Financial Pending info (N240)
    * internal_pending - Returns Serasa's Internal Pending info (N230)
    * company_state - Returns Serasa's Company State info (N200)
    * check_consult - Returns Serasa's Check Consult info (N440)
    * stolen_document - Returns Serasa's Stolen Document info (N210)
    * qsadmin - Returns Serasa's QSA Admins info (N705)
    * board_view - Returns Serasa's Protest info (N700)
    """

    request_params: Optional[str] = None
    request_datetime: Optional[datetime] = None
    total_records: Optional[int] = None
    data: Optional[Dict[Any, Any]] = None


class SerasaSerializer(BaseSchema):
    request_params = fields.String(allow_none=True)
    request_datetime = fields.DateTime(allow_none=True)
    total_records = fields.Integer(allow_none=True)
    payload = fields.Dict(allow_none=True)
    data = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> SerasaData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = SerasaData(**data)
        new_data.datasource_base_url = Serasa.base_url
        logger.warning(
            "Serasa Prospecting is in Working-in-Progress state. "
            "USE THIS INFORMATION WITH CAUTION."
        )
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class Serasa(BaseSnatch):
    default_timeout: int = 60
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_serasa_url"
    authorization_token_key: str = "snatch.serasa_secret_token"
    serializer_class: Type[Schema] = SerasaSerializer
