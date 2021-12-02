import shelve
import json
import time
from pathlib import Path
import re
from shelve import DbfilenameShelf
from typing import Dict, Any

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime as etld_lib_datetime
global count_items_added_to_shelve
global count_items_added_to_shelve_display_progress
global shelve_database
global shelve_software_unique_database
global shelve_software_assetid_database
global shelve_temp_database
global json_dir
global json_dir_search_glob
global json_file_list
global software_full_name_dict


def transform_epoch_dates(item):
    item['sensor_lastVMScanDate'] = ""
    item['sensor_lastComplianceScanDate'] = ""
    item['sensor_lastFullScanDate'] = ""
    item['agent_lastActivityDate'] = ""
    item['agent_lastCheckedInDate'] = ""
    item['agent_lastInventoryDate'] = ""
    item['inventory_createdDate'] = ""
    item['inventory_lastUpdatedDate'] = ""
    if 'sensor' in item.keys() and item['sensor'] is not None:
        if 'lastVMScan' in item['sensor']:
            item['sensor_lastVMScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVMScan'])
        if 'lastComplianceScan' in item['sensor']:
            item['sensor_lastComplianceScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastComplianceScan'])
        if 'lastFullScan' in item['sensor']:
            item['sensor_lastFullScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastFullScan'])

    if 'agent' in item.keys() and item['agent'] is not None:
        if 'lastActivity' in item['agent']:
            item['agent_lastActivityDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastActivity'])
        if 'lastCheckedIn' in item['agent']:
            item['agent_lastCheckedInDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastCheckedIn'])
        if 'lastInventory' in item['agent']:
            item['agent_lastInventoryDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastInventory'])

    if 'inventory' in item.keys() and item['inventory'] is not None:
        if 'created' in item['inventory']:
            item['inventory_createdDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['created'])
        if 'lastUpdated' in item['inventory']:
            item['inventory_lastUpdatedDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['lastUpdated'])
    return item


def transform_json_item_to_shelve(item=None, sd=None, sd_file=None):
    global count_items_added_to_shelve
    global count_items_added_to_shelve_display_progress
    global json_dir
    global json_dir_search_glob

    item_key = item['assetId']
    item = transform_epoch_dates(item)
    max_retries = 5
    for i in range(max_retries):
        try:
            sd[str(item_key)] = item
            count_items_added_to_shelve += 1
            count_items_added_to_shelve_display_progress += 1
            if count_items_added_to_shelve_display_progress > 9999:
                count_items_added_to_shelve_display_progress = 0
                etld_lib_functions.logger.info(f"asset inventory shelve records written: "
                                               f"{count_items_added_to_shelve:,}")

        except Exception as e:
            time.sleep(1)
            etld_lib_functions.logger.warning(
                f"Retry #{i + 1:02d} writing assetId {item_key} to {str(sd_file)} Exception {e}")
            time.sleep(5)
            continue
        else:
            break # Success
    else:
        etld_lib_functions.logger.error(f"max retries attempted: {max_retries}"
                                        f"error writing assetId:{item_key} "
                                        f"to file: {str(shelve_database)} ")
        exit(1)

    return True


def asset_inventory_shelve_software(item):
    global shelve_software_unique_database
    global shelve_software_assetid_database

    if item['softwareListData'] is not None:
        with shelve.open(str(shelve_software_unique_database),
                         flag='c') as software_unique_dict:
            with shelve.open(str(shelve_software_assetid_database),
                             flag='c') as software_assetid_dict:
                for software_item in item['softwareListData']['software']:
                    if 'fullName' in software_item:
                        assetid_fullname = f"{item['assetId']}_{software_item['fullName']}"
                        if assetid_fullname not in software_assetid_dict:
                            software_assetid_dict[assetid_fullname] = ""

                        fullname = f"{software_item['fullName']}"
                        if fullname not in software_assetid_dict:
                            if 'lifecycle' in software_item:
                                software_unique_dict[fullname] = software_item['lifecycle']
                            else:
                                software_unique_dict[fullname] = {'gaDate': None, 'eolDate': None, 'eosDate': None,
                                                                  'stage': None,
                                                                  'lifeCycleConfidence': 'Not Available QETL',
                                                                  'eolSupportStage': '', 'eosSupportStage': ''}


def asset_inventory_shelve():
    global count_items_added_to_shelve
    global shelve_database
    global shelve_temp_database
    global json_dir
    global json_dir_search_glob
    global json_file_list

    try:
        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob), reverse=True)
        for json_file in json_file_list:
            with open(str(json_file), "r", encoding='utf-8') as read_file:
                sd_temp: DbfilenameShelf
                with shelve.open(str(shelve_temp_database), flag='n') as sd_temp:
                    sd_temp = json.load(read_file)
                    with shelve.open(str(shelve_database), flag='c') as sd:
                        for item in sd_temp['assetListData']['asset']:
                            asset_id = str(item['assetId'])
                            if asset_id in sd:
                                pass
                                # etld_lib_functions.logger.info(f"Asset already exists in shelve: {asset_id}")
                            else:
                                transform_json_item_to_shelve(item, sd, str(shelve_database))
                                asset_inventory_shelve_software(item)

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
        exit(1)


def end_msg_asset_inventory_shelve():
    global count_items_added_to_shelve
    global json_dir_search_glob
    global json_dir
    global json_file_list

    etld_lib_functions.logger.info(
        f"count host ids added to shelve: {count_items_added_to_shelve:,} for {str(shelve_database)}")
    for json_file in json_file_list:
        etld_lib_functions.log_file_info(json_file, 'in')
    etld_lib_functions.log_dbm_info(str(shelve_database))
    etld_lib_functions.log_file_info(str(shelve_database))
    etld_lib_functions.log_file_info(str(shelve_database))
    etld_lib_functions.log_file_info(str(shelve_software_unique_database))
    etld_lib_functions.log_file_info(str(shelve_software_assetid_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_unique_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_assetid_database))

    etld_lib_functions.logger.info(f"end")


def start_msg_asset_inventory_shelve():
    etld_lib_functions.logger.info("start")


def setup_shelve_vars():
    global count_items_added_to_shelve
    global count_items_added_to_shelve_display_progress
    global shelve_database
    global shelve_software_unique_database
    global shelve_software_assetid_database
    global shelve_temp_database
    global json_dir
    global json_dir_search_glob

    count_items_added_to_shelve = 0
    count_items_added_to_shelve_display_progress = 0
    shelve_database = etld_lib_config.asset_inventory_shelve_file
    shelve_software_unique_database = etld_lib_config.asset_inventory_shelve_software_unique_file
    shelve_software_assetid_database = etld_lib_config.asset_inventory_shelve_software_assetid_file
    shelve_temp_database = etld_lib_config.asset_inventory_temp_shelve_file
    json_dir = etld_lib_config.asset_inventory_json_dir
    json_dir_search_glob = 'asset_inventory_utc*.json'


def main():
    start_msg_asset_inventory_shelve()
    setup_shelve_vars()
    asset_inventory_shelve()
    end_msg_asset_inventory_shelve()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_shelve')
    etld_lib_config.main()
    main()
