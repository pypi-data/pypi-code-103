import csv
import shelve
import re
import dbm.gnu
import pickle
import gzip
import json
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_host_ids_written
global count_host_qids_written
global asset_inventory_item
global asset_inventory_csv_truncate_cell_limit
global asset_inventory_csv_file
global asset_inventory_csv_software_unique_file
global asset_inventory_csv_software_assetid_file

# TODO In prepare_csv_cell, compiled regex slowed program, investigate why
# prepare_date_compile_regex = re.compile(r'(^.*)(T)(.*)(\.)')
# prepare_column_names_compile_regex = re.compile(r'(^.*)(Date|lastBoot)(.*$)')
# elif re.match(prepare_column_names_compile_regex, csv_column):  # Prepare dates for use in Excel or Database
# csv_cell = re.sub(prepare_date_compile_regex, '\g<1> \g<3>', csv_cell)


def prepare_csv_cell(csv_cell, csv_column, present_cell_as_json=False):
    if csv_cell is None:
        csv_cell = ""
    elif 'Date' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
        csv_cell = re.sub("\\..*$", "", csv_cell)
    elif 'lastBoot' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
        csv_cell = re.sub("\\..*$", "", csv_cell)
    elif isinstance(csv_cell, int):
        csv_cell = str(csv_cell)
    elif not isinstance(csv_cell, str):  # Flatten Nested JSON into cell
        if present_cell_as_json:
            csv_cell = json.dumps(csv_cell)
        else:
            flatten = etld_lib_functions.flatten_nest(csv_cell)
            csv_cell = ""
            csv_list = []
            for key in flatten:
                csv_list.append(f"{key}:{flatten[key]}")
            csv_cell = '\n'.join(csv_list)

    return csv_cell


def asset_inventory_to_csv():  # Create CSV File from Shelve Database
    global count_host_ids_written
    global asset_inventory_csv_file
    global asset_inventory_item

    asset_inventory_csv_file = etld_lib_config.asset_inventory_csv_file     # Output CSV File

    present_csv_cell_as_json = False
    if etld_lib_config.asset_inventory_present_csv_cell_as_json is True:
        present_csv_cell_as_json = True

    csv_columns = etld_lib_functions.asset_inventory_csv_columns()
    count_host_ids_written = 0
    count_host_ids_written_display_progress = 0
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(asset_inventory_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_row = csv_headers.copy()
            # Iterate through Shelve Database using dbm.gnu.open for speed.
            etld_lib_functions.logger.info(f"shelve db filename: {str(etld_lib_config.asset_inventory_shelve_file)}")
            with dbm.gnu.open(str(etld_lib_config.asset_inventory_shelve_file), 'rf') as shelve_database:
                #etld_lib_functions.logger.info(f"shelve db count: {len(shelve_database)}")
                shelve_database_item = shelve_database.firstkey()
                while shelve_database_item is not None:
                    asset_inventory_item = pickle.loads(shelve_database[shelve_database_item])
                    truncated_field_list = ""
                    for csv_column in csv_columns:  # Iterate through expected columns (contract)
                        if csv_column in asset_inventory_item.keys():  # Iterate through columns found in Shelve
                            asset_inventory_item[csv_column] = prepare_csv_cell(asset_inventory_item[csv_column],
                                                                                csv_column, present_csv_cell_as_json)
                            if etld_lib_config.asset_inventory_csv_truncate_cell_limit is False:
                                csv_row[csv_column] = asset_inventory_item[csv_column]
                            else:
                                csv_row[csv_column], truncated_field_list = \
                                    etld_lib_functions.truncate_csv_cell(
                                                  max_length=etld_lib_config.asset_inventory_csv_truncate_cell_limit,
                                                  csv_cell=asset_inventory_item[csv_column],
                                                  truncated_field_list=truncated_field_list,
                                                  csv_column=csv_column)
                        else:
                            csv_row[csv_column] = ""  # Ensure blank is added to each required empty field
                            if csv_column == 'TRUNCATED_FIELD_LIST':
                                asset_inventory_item[csv_column] = truncated_field_list
                                csv_row[csv_column] = asset_inventory_item[csv_column]
                    # Write CSV row, Prepare for next row.
                    writer.writerow(csv_row)

                    count_host_ids_written = count_host_ids_written + 1
                    count_host_ids_written_display_progress = count_host_ids_written_display_progress + 1
                    if count_host_ids_written_display_progress > 9999:
                        count_host_ids_written_display_progress = 0
                        etld_lib_functions.logger.info(f"csv rows written: {count_host_ids_written}")

                    csv_row = csv_headers.copy()
                    shelve_database_item = shelve_database.nextkey(shelve_database_item)

    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(asset_inventory_csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def asset_inventory_software_assetid_to_csv():  # Create CSV File from Shelve Database

    csv_file = etld_lib_config.asset_inventory_csv_software_assetid_file
    asset_inventory_shelve_file = etld_lib_config.asset_inventory_shelve_software_assetid_file
    csv_columns = etld_lib_functions.asset_inventory_software_assetid_csv_columns()
    count_csv_records_written = 0
    count_csv_records_written_display_progress = 0
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_row = csv_headers.copy()
            number_of_csv_columns = len(csv_columns)
            # Iterate through Shelve Database using dbm.gnu.open for speed.
            etld_lib_functions.logger.info(f"shelve db filename: {str(asset_inventory_shelve_file)}")
            with dbm.gnu.open(str(asset_inventory_shelve_file), 'rf') as shelve_database:
                shelve_database_item = shelve_database.firstkey()
                while shelve_database_item is not None:
                    shelve_item = shelve_database_item.decode('utf-8').split("_", 1)
                    shelve_item.insert(0, count_csv_records_written)
                    if len(shelve_item) == number_of_csv_columns:
                        shelve_item_count = 0
                        csv_row = {}
                        for csv_column in csv_columns:
                            csv_row[csv_column] = str(shelve_item[shelve_item_count])
                            shelve_item_count += 1
                        writer.writerow(csv_row)
                        count_csv_records_written += 1
                        count_csv_records_written_display_progress += 1
                        if count_csv_records_written_display_progress > 9999:
                            count_csv_records_written_display_progress = 0
                            etld_lib_functions.logger.info(f"csv rows written: {count_csv_records_written}")
                    else:
                        etld_lib_functions.logger.error(
                            f"Error encountered : {shelve_item}, please retry after fixing error")
                        exit(1)

                    csv_row = csv_headers.copy()
                    shelve_database_item = shelve_database.nextkey(shelve_database_item)

    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def asset_inventory_software_unique_to_csv():  # Create CSV File from Shelve Database

    csv_file = etld_lib_config.asset_inventory_csv_software_unique_file
    asset_inventory_shelve_file = etld_lib_config.asset_inventory_shelve_software_unique_file
    csv_columns = etld_lib_functions.asset_inventory_software_unique_csv_columns()
    count_csv_records_written = 0
    count_csv_records_written_display_progress = 0
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_row = csv_headers.copy()
            number_of_csv_columns = len(csv_columns)
            # Iterate through Shelve Database using dbm.gnu.open for speed.
            etld_lib_functions.logger.info(f"shelve db filename: {str(asset_inventory_shelve_file)}")
            with dbm.gnu.open(str(asset_inventory_shelve_file), 'rf') as shelve_database:
                shelve_database_key = shelve_database.firstkey()
                while shelve_database_key is not None:
                    shelve_key = shelve_database_key.decode('utf-8')
                    shelve_database_dict = pickle.loads(shelve_database[shelve_database_key])
                    csv_row[csv_columns[0]] = shelve_key
                    for csv_column in csv_columns[1:]:
                        if csv_column in shelve_database_dict.keys():
                            csv_row[csv_column] = shelve_database_dict[f"{csv_column}"]
                            csv_row[csv_column] = prepare_csv_cell(csv_row[csv_column], csv_column)
                        else:
                            csv_row[csv_column] = ''

                    writer.writerow(csv_row)
                    count_csv_records_written += 1
                    count_csv_records_written_display_progress += 1
                    if count_csv_records_written_display_progress > 9999:
                        count_csv_records_written_display_progress = 0
                        etld_lib_functions.logger.info(f"csv rows written: {count_csv_records_written}")

                    csv_row = csv_headers.copy()
                    shelve_database_key = shelve_database.nextkey(shelve_database_key)

    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def start_msg_asset_inventory_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_asset_inventory_csv():
    global count_host_ids_written
    global count_host_qids_written
    etld_lib_functions.logger.info(f"count host ids written (hosts) written to csv: {count_host_ids_written:,}")
    etld_lib_functions.log_file_info(etld_lib_config.asset_inventory_shelve_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.asset_inventory_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.asset_inventory_csv_file)
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_asset_inventory_csv()
    asset_inventory_software_unique_to_csv()
    asset_inventory_software_assetid_to_csv()
    asset_inventory_to_csv()
    end_msg_asset_inventory_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_csv')
    etld_lib_config.main()
    main()
