import logging

logger = logging.getLogger('json_to_table')
# logger.setLevel(logging.WARNING)
import pandas
from .typestools import checkStr


class JsonToTable:
    dataFrame_list_list = dict()  # dict of each generated table

    table_list = dict()  # dict of each generated table
    table_field_list = dict()  # list of current field for each generated table
    table_key_list = dict()  # list of key list use for a table
    inputJson = dict()
    merge_list = True
    root_type = None

    def __init__(self, merge_list=True, merge_dict=True):
        self.dataFrame_list_list = dict()
        self.table_list = dict()  # dict of each generated table
        self.table_field_list = dict()  # list of current field for each generated table
        self.table_key_list = dict()
        self.inputJson = dict()
        self.merge_list = merge_list
        self.merge_dict = merge_dict
        self.root_type = None
        inputJson = dict()

    def parseDict(self, x, preFix="", list_pref="", prev_field_list=dict(), list_ID=""):
        logger.debug(f"start parseDict preFix:{preFix}  ")

        list_keys = []
        field_list = prev_field_list
        for key, value in x.items():
            logger.debug(f"key {key} type : {type(value)}")
            if 'dict' in str(type(value)):  # TODO replace by is instance
                sub_list_ID = ""
                if self.merge_dict == False:
                    sub_list_ID = list_ID
                field_list = {**field_list,
                              **self.parseDict(value, preFix + key + ".", prev_field_list=dict(), list_ID=sub_list_ID,list_pref=list_pref)}

            else:
                if ('list' in str(type(value))) or ('tuple' in str(type(value))): #TODO use isinstnace
                    list_keys.append(key)
                    logger.debug("case List key" + key)

                else:
                    field_list[preFix + key] = checkStr(value)
        if len(list_keys) > 0:
            for key_for_list in list_keys:
                if self.merge_dict == False:
                    full_key = preFix + key_for_list
                else:
                    full_key = list_ID + key_for_list
                logger.debug(f"case list key not NA preFix:{preFix} list_key:{full_key} key:{key} ")
                self.table_field_list[full_key] = field_list.copy()
                new_table = self.parseList(x[key_for_list], preFix + key_for_list + ".",
                                           prev_field_list=self.table_field_list[full_key], list_pref=list_pref)
                if full_key in self.table_list:
                    self.table_list[full_key] = {**self.table_list[full_key], **new_table}
                else:
                    self.table_list[full_key] = new_table

        logger.debug(f"return for parseDict {str(field_list)}")
        return (field_list)

    def parseList(self, x, preFix="", prev_field_list=dict(), list_pref="", list_ID="root"):

        logger.debug("start parseList ")
        logger.debug(f"parseList {str(x)} prefix{preFix}")
        logger.debug(f"prev_field_list {str(prev_field_list)} ")
        table_dict = dict()
        i = 0
        for value in x:
            field_list = prev_field_list
            i = i + 1
            if self.merge_list:
                list_ID = preFix
            else:
                list_ID = preFix + "#" + str(i)

            if 'dict' in str(type(value)):  # TODO use isinstance
                field_list = {**field_list, **self.parseDict(value, preFix, list_pref=list_pref + "_" + str(i),
                                                             prev_field_list=prev_field_list, list_ID=list_ID)}

            else:
                if ('list' in str(type(value))) or ('tuple' in str(type(value))):
                    field_list = {**field_list, **self.parseList(value, preFix, prev_field_list=prev_field_list,
                                                                 list_pref=list_pref + "_" + str(i))}
                else:
                    field_list[list_ID] = checkStr(value)
            logger.debug(f"field_list {str(field_list)}")
            first_key = list(field_list.keys())[0]
            if "list_" in first_key:
                logger.debug(f"List in list key {first_key} ")
                table_dict = {**table_list, **field_list}
            else:
                logger.debug(f"add list line  {'list_' + list_pref + '_' + str(i)} ")
                table_dict['list_' + list_pref + "_" + str(i)] = field_list.copy()
        logger.debug(f"return from parseList {str(table_dict)} ")
        return (table_dict)

    def parseJson(self, x):

        if isinstance(x, list):
            y = dict({'root': x})
            self.root_type = 'list'
            self.inputJson = y
            res = self.parseDict(y, prev_field_list=dict())
        else:
            self.root_type = 'dict'
            self.inputJson = x
            res = self.parseDict(x, prev_field_list=dict())
        dataFrame_list_list = dict()
        for tablekey in self.table_list:
            logger.info(f"table {tablekey}")

            dataFrame_list_list[tablekey] = pandas.DataFrame.from_dict(self.table_list[tablekey], orient='index')
            logger.debug(dataFrame_list_list[tablekey])
        self.dataFrame_list_list = dataFrame_list_list
        return dataFrame_list_list

"""
def insert_dict_in_dict(tab_split, cur_json, new_dict):
    insert a dict in another dict based on the path given in tab_split.
    If nodes re missing it should create it

    depth = len(tab_split)
    node = cur_json
    for i in range(depth):
        node_name = tab_split[i]
        if node_name in node:
            node = node[node_name]
        else:
            new_node = dict()
            node[node_name] = new_node
            node = new_node
    node.update(**new_dict)

    return cur_json
"""