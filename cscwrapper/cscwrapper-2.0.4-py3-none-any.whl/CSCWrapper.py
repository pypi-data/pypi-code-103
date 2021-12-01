
import os
import xmltodict
from requests.sessions import OrderedDict
from enum import Enum
from jinja2 import Environment, PackageLoader, select_autoescape
from cscwrapper.APIHandler import APIHandler


env = Environment(loader=PackageLoader("cscwrapper.CSC"), autoescape=select_autoescape())

class CSCWrapper(APIHandler):
    """
    
    """
    headers = {"content-type" : "text/xml"}

    def __init__(self, host, guid, contact_no, logging=True):
        self.__guid = guid
        self.__contact_no = contact_no
        self._api_handler = APIHandler(
            host,
            headers=self.headers,
            logging=logging,
        )

    def create_filing(self, filing: dict, log_config: dict = None, *args, **kwargs):
        return self.send_request("POST", "CreateFiling.xml", filing, log_config=log_config)

    def validate_filing(self, order_id, log_config: dict = None):
        params = {'order_id': order_id}
        return self.send_request("POST", "ValidateFiling.xml", params, log_config=log_config)
    
    def update_filing(self, order_id, update_filing, log_config: dict = None):
        update_filing['order_id'] = order_id
        return self.send_request("POST", "UpdateFiling.xml", update_filing, log_config=log_config)
    
    def approve_order(self, order_id, log_config: dict = None):
        params = {'order_id': order_id}
        return self.send_request("POST", "ApproveOrder.xml", params, log_config=log_config)

    def continue_filing(self, order_id, log_config: dict = None):
        params = {'order_id': order_id}
        return self.send_request("POST", "ContinueFiling.xml", params, log_config=log_config)

    def terminate_filing(self, order_id, log_config: dict = None):
        params = {'order_id': order_id}
        return self.send_request("POST", "TerminateFiling.xml", params, log_config=log_config)

    def get_order_info(self, order_id: int, log_config: dict = None) -> OrderedDict:
        params = {'order_id': order_id}
        return self.send_request("POST", "GetOrderInformation.xml", params, log_config=log_config)

    def get_changed_orders(self, status, from_date, log_config: dict = None) -> OrderedDict:
        params = {
            'status': status,
            'from_date': from_date,
        }
        return self.send_request("POST", "GetChangedOrders.xml", params, log_config=log_config)

    def upload_attachment(
        self,
        order_id,
        content_type,
        description,
        attachment,
        log_config: dict = None
    ):
        """
        Uploads file to CSC servers

        params:
            order_id: int
            content_type: str
            description: str
            file: base64 str
        
        returns:
            response: SoapResult
        """
        params = {
            'order_id': order_id,
            'content_type': content_type,
            'description': description,
            'attachment': attachment
        }
        return self.send_request("POST", "UploadAttachment.xml", params, log_config=log_config)

    def get_attachment(self, attachment_id, log_config: dict = None) -> OrderedDict:
        return self.send_request("POST", "GetAttachment.xml", {'attachment_id': attachment_id}, log_config=log_config)

    def get_available_searches(self, state, is_online, log_config: dict = None):
        params = {
            'state': state,
            'is_online': is_online,
        }
        return self.send_request("POST", "AvailableSearches.xml", params, log_config=log_config)

    def get_jurisdictions(self, state, log_config: dict = None):
        return self.send_request("POST", "GetJurisdictions.xml", {'state': state}, log_config=log_config)

    def get_summary_results(self, order_id, log_config: dict = None):
        params = {
            'order_id': order_id
        }
        return self.send_request("POST", "GetSummaryResults.xml", params, log_config=log_config)
    
    def get_detail_results(self, order_id, log_config: dict = None):
        params = {
            'order_id': order_id
        }
        return self.send_request("POST", "GetDetailResults.xml", params, log_config=log_config)
    
    def get_report(self, order_id, report_type, log_config: dict = None):
        params = {
            'order_id': order_id,
            'report_type': report_type
        }
        return self.send_request("POST", "GetReport.xml", params, log_config=log_config)

    def get_documents(self, order_id, selected_results=None, log_config: dict = None):
        params = {
            'order_id': order_id,
            'selected_results': selected_results
        }
        return self.send_request("POST", "GetDocuments.xml", params, log_config=log_config)
    
    def set_selected_results(self, result_type, order_id, row_ids=[], log_config: dict = None):
        if result_type == 'summary':
            template = 'SetSelectedSummaryResults.xml'
        elif result_type == 'detail':
            template = 'SetSelectedDetailResults.xml'
        else:
            raise ValueError('Invalid result type')
        
        params = {
            'order_id': order_id,
            'row_ids': row_ids
        }
        return self.send_request("POST", template, params, log_config=log_config)
    
    def submit_search(self, is_offline, params, log_config: dict = None):
        if is_offline:
            template = 'SubmitOfflineSearch.xml'
        else:
            template = 'SubmitOnlineSearch.xml'
        
        return self.send_request("POST", template, params, log_config=log_config)
        
    def send_request(self, method, template_name, params, log_config: dict = None):
        params['contact_no'] = self.__contact_no
        params['guid'] = self.__guid
        template = env.get_template(template_name)
        payload = template.render(**params)

        return xmltodict.parse(self._api_handler._send_request(method, payload, log_config=log_config))