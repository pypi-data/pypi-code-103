import base64
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

from wkfs_wrapper.APIHandler import APIHandler
from wkfs_wrapper.constants import BASE_DIR
import logging

env = Environment(
    loader=FileSystemLoader(f"{BASE_DIR}/../templates"), autoescape=select_autoescape()
)

LOGGER = logging.getLogger("roor")

class WKFSAdapter:
    def __init__(self, host, logging=True):
        self._api_handler = APIHandler(
            host,
            headers={},
            logging=logging,
        )

    def generate_package(
        self,
        transaction_data_json_input: str,
        e_sign: bool = False,
        product: str = None,
        log_config: dict = None,
        access_token: str = None,
        wkfs_config: dict = None
    ) -> dict:
        """
        Call the `send` API for generating the document.

        :param
            transaction_data_json_input: Json input from the calling application to generate the transaction xml
            e_sign: Indicating whether e signature co-ordinates should be part of response
            product: The product for which documents are generated.
            access_token: The access token required to authenticate the caller.

        """

        # TODO: Plug in the Json Schema validator here?

        # with open(f"{BASE_DIR}/../wkfs_config.json", "r", encoding="utf-8") as file:
        #     wkfs_payload = json.load(file)

        #wkfs_payload = json.load(wkfs_config)

        wkfs_id = wkfs_config["wkfs_id"]
        products = wkfs_config["products"]
        account_id = wkfs_config["account_id"]
        wkfs_product = None
        wkfs_xml = None
        for config_product in products:
            wkfs_product = config_product.get("name")
            if wkfs_product == product:
                wkfs_package = config_product.get("wkfs_package")
                wkfs_xml = config_product.get("wkfs_xml")
                break

        if None in [wkfs_package, wkfs_xml]:
            raise Exception("Unable to read product configuration!")
        payload = {}
        generate = {}
        request = {}

        request["documentFormat"] = "PDF"
        if e_sign:
            eSignatureAndFieldSupport = {
                "eSignatureCoordinatesOnly": True,
                "eSignatureDateSupport": True,
                "eSignatureTooltip": "Kindly Sign here",
                "eSignatureInitialsTooltip": "Kindly put your initials here",
                "nonSignatureFieldCoordinatesOnly": True,
                "eSignatureWKES": False,
            }
            request["eSignatureAndFieldSupport"] = eSignatureAndFieldSupport

        template = env.get_template(wkfs_xml)

        data_dict = json.loads(transaction_data_json_input)
        transaction_xml_payload = template.render(**data_dict)

        transaction_xml_payload_bytes = transaction_xml_payload.encode("utf-8")

        base64_bytes = base64.b64encode(transaction_xml_payload_bytes)
        transaction_data_base64 = base64_bytes.decode("utf-8")

        request["transactionData"] = transaction_data_base64
        request["contentIdentifier"] = f"expere://{wkfs_id}/{wkfs_package}"
        generate["request"] = request
        payload["generate"] = generate

        headers = self._api_handler._headers
        headers["Authorization"] = f"Bearer {access_token}"
        headers["Content-Type"] = "application/json"
        response = self._api_handler.send_request(
            "POST",
            f"/DocumentService/api/v1/Document/account/{account_id}/generate-synchronous",
            payload=json.dumps(payload),
            log_config=log_config,
            headers=headers,
        )

        LOGGER.debug(
            f'generate_package from wkfs wrapper completed'
        )
        return json.loads(response)

    def get_access_token(
        self, grant_type: str, client_id: str, scope: str, wkfs_client_certificate: str
    ):
        """
        Call the `send` API for getting the access token

        :param
            grant_type: Required field for WKFS get_access_token
            client_id: Required field for WKFS get_access_token
            scope: Required field for WKFS get_access_token
            wkfs_client_certificate: Required header field for WKFS get_access_token. Client certificate in base64 format
        """
        if None in [grant_type, client_id, scope, wkfs_client_certificate]:
            raise Exception(
                f"Failed to get access token. Required fields missing: grant_type, client_id, scope, wkfs_client_certificate"
            )

        headers = self._api_handler._headers
        payload = {"grant_type": grant_type, "client_id": client_id, "scope": scope}
        headers["WKFS-ClientCertificate"] = wkfs_client_certificate
        response = self._api_handler.send_request(
            "POST", f"/STS/connect/token", payload=payload, headers=headers
        )
        LOGGER.debug(
            f"get_access_token from wkfs wrapper completed!"
        )
        return response
