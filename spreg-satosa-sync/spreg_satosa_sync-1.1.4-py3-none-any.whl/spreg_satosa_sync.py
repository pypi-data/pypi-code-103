#!/usr/bin/env python3

import argparse
import base64
import hashlib

import pymongo
import requests
import yaml
from pymongo.errors import OperationFailure
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def get_collection(cfg):
    client = pymongo.MongoClient(cfg["database"]["connection_string"])
    database_name = cfg["database"]["database_name"]
    collection_name = cfg["database"]["collection_name"]
    return client[database_name][collection_name]


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_filepath", type=str, help="path_to_config_file")
    arguments = parser.parse_args()
    with open(arguments.config_filepath, "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        return cfg


def get_attr_perun_names(cfg):
    names = []
    for attribute in cfg["attributes"].values():
        if isinstance(attribute, list):
            for val in attribute:
                names.append(val)
        else:
            names.append(attribute)
    return names


def get_data(cfg):
    rpc_url = cfg["rpc"]["perun_url"]
    rpc_facilities = "{}json/searcher/getFacilities".format(rpc_url)
    rpc_username = cfg["rpc"]["perun_user"]
    rpc_password = cfg["rpc"]["perun_password"]
    resp = requests.post(
        rpc_facilities,
        json={
            "attributesWithSearchingValues": {
                cfg["attributes"]["rp_type"]: cfg["rp_type_attr_value"],
                cfg["attributes"]["proxy_identifier"]: cfg["proxy_identifier_value"],
            }
        },
        auth=(rpc_username, rpc_password),
    )
    if resp.status_code != 200:
        print("facility invalid response")
        return "INVALID RESPONSE"
    facilities_list = resp.json()
    present_client_ids = []
    collection = get_collection(cfg)
    for facility in facilities_list:
        resp = requests.post(
            "{}json/attributesManager/getAttributes".format(cfg["rpc"]["perun_url"]),
            json={"facility": facility["id"], "attrNames": get_attr_perun_names(cfg)},
            auth=(rpc_username, rpc_password),
        )
        if resp.status_code != 200:
            print("attributes invalid response")
            return "INVALID RESPONSE"
        facility_attrs = resp.json()
        attrs_dict = get_attr_dict(cfg, facility_attrs)
        print("Processing client_id: {}.".format(attrs_dict["client_id"]))
        try:
            result = collection.replace_one(
                {"client_id": attrs_dict["client_id"]}, attrs_dict, True
            )
            if result.upserted_id:
                print("Client {} upserted.".format(attrs_dict["client_id"]))
            else:
                print("Client {} updated.".format(attrs_dict["client_id"]))

        except OperationFailure as e:
            print(
                "Processing of client_id failure code: {} details: {}".format(
                    attrs_dict["client_id"], e.code, e.details
                )
            )
        present_client_ids.append(attrs_dict["client_id"])
    if cfg["delete_not_present_clients"]:
        try:
            print("Processing delete of not present clients.")
            result = collection.delete_many({"client_id": {"$nin": present_client_ids}})
            print("Deleted {} not present clients.".format(result.deleted_count))
        except OperationFailure as e:
            print(
                "Processing of delete not present clients failure code: {} details: {}".format(
                    e.code, e.details
                )
            )


def get_issue_refresh_tokens_value(cfg, facility_attrs):
    for attr in facility_attrs:
        attr_perun_name = attr["namespace"] + ":" + attr["baseFriendlyName"]
        if attr_perun_name == cfg["attributes"]["issue_refresh_tokens"]:
            if attr["value"] == "true":
                return True
            return False


def get_attr_dict(cfg, facility_attrs):
    result = {}
    for key, value in cfg["static_attributes"].items():
        result[key] = value

    for attr in facility_attrs:
        attr_perun_name = attr["namespace"] + ":" + attr["baseFriendlyName"]
        for key, value in cfg["attributes"].items():
            if isinstance(value, list) and attr_perun_name in value:
                if key in result:
                    result[key].append(attr["value"])
                else:
                    result[key] = [attr["value"]]
            elif value == attr_perun_name:
                if key == "redirect_uris":
                    if attr["value"]:
                        temp = []
                        for uri in attr["value"]:
                            temp.append([uri, None])
                        result[key] = temp
                elif key == "client_secret":
                    result[key] = (
                        None
                        if attr["value"] is None or attr["value"] == "null"
                        else decrypt_secret(attr["value"], cfg["encryption_key"])
                    )
                elif key == "flow_types":
                    issue_refresh_tokens = get_issue_refresh_tokens_value(
                        cfg, facility_attrs
                    )
                    grant_types, response_types = set_grant_and_response_types(
                        attr["value"], issue_refresh_tokens
                    )
                    result["grant_types_supported"] = grant_types
                    result["response_types"] = response_types
                elif key in [
                    "client_name",
                    "tos_uri",
                    "policy_uri",
                    "logo_uri",
                    "client_uri",
                ]:
                    if not attr["value"] or isinstance(attr["value"], str):
                        result[key] = attr["value"]
                    else:
                        for lan, trans in attr["value"].items():
                            if key not in result:
                                result[key] = trans
                            result[key + "#" + lan] = trans
                elif key == "code_challenge_type":
                    if attr["value"] and attr["value"] != "none":
                        result["pkce_essential"] = True
                elif key == "post_logout_redirect_uri":
                    result[key] = [attr["value"], None]
                elif key not in ["master_proxy_identifier", "proxy_identifier", "rp_type"]:
                    result[key] = attr["value"]
    return result


def set_grant_and_response_types(flow_types_list, issue_refresh_tokens):
    grant_types = set()
    response_types = set()

    authorization_code = "authorization code"
    device = "device"
    implicit = "implicit"
    hybrid = "hybrid"

    grant_authorization_code = "authorization_code"
    grant_implicit = "implicit"
    grant_device = "urn:ietf:params:oauth:grant-type:device_code"
    grant_hybrid = "hybrid"
    grant_refresh_token = "refresh_token"

    response_code = "code"
    response_token = "token"
    response_id_token = "id_token"
    response_token_id_token = response_token + " " + response_id_token
    response_id_token_token = response_id_token + " " + response_token
    response_code_id_token = response_code + " " + response_id_token
    response_code_token = response_code + " " + response_token
    response_code_token_id_token = response_code_token + " " + response_id_token
    response_code_id_token_token = response_code_id_token + " " + response_token

    response_type_auth_code = {response_code}
    response_type_implicit = {
        response_id_token,
        response_token,
        response_id_token_token,
        response_token_id_token,
    }
    response_type_hybrid = {
        response_code_token,
        response_code_id_token,
        response_code_id_token,
        response_code_id_token_token,
        response_code_token_id_token,
    }

    if authorization_code in flow_types_list:
        grant_types.add(grant_authorization_code)
        response_types.update(response_type_auth_code)
    if implicit in flow_types_list:
        grant_types.add(grant_implicit)
        response_types.update(response_type_implicit)
    if hybrid in flow_types_list:
        grant_types.add(grant_hybrid)
        grant_types.add(grant_authorization_code)
        response_types.update(response_type_hybrid)
    if device in flow_types_list:
        grant_types.add(grant_device)
    if issue_refresh_tokens:
        grant_types.add(grant_refresh_token)
    return list(grant_types), list(response_types)


def decrypt_secret(client_secret, encryption_key):
    encryption_key = generate_secret_key_spec(encryption_key)
    decoded = base64.urlsafe_b64decode(client_secret)
    cipher = AES.new(encryption_key, AES.MODE_ECB)
    return unpad(cipher.decrypt(decoded), 16).decode("utf-8")


def generate_secret_key_spec(secret):
    secret = fix_secret(secret)
    key = secret.encode("utf-8")
    my_hash = hashlib.sha1()
    my_hash.update(key)
    key = my_hash.digest()
    return key[0:16]


def fix_secret(secret):
    if len(secret) < 32:
        missing_length = 32 - len(secret)
        for i in range(missing_length):
            secret += "A"
    return secret[0:32]


def main():
    get_data(get_config())


if __name__ == "__main__":
    main()
