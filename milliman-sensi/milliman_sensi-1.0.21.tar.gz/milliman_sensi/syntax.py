import os
import re
import numpy as np

from objectpath import *

import pandas as pd

# IR -> Nominal_rates
# RIR -> Real_rates
# EQ -> Equity
# RE -> Real_estate
# CRED -> Credit
# FX -> FX_rate
MODEL_DIR_NAMES = {'IR': 'Nominal_rates',
                   'RIR': 'Real_rates',
                   'EQ': 'Equity',
                   'RE': 'Real_estate',
                   'CRED': 'Credit',
                   'FX': 'FX_rate'}

FILE_MARK = "file::"


# Custom Exception class for sensi validation
class SensiSyntaxError(Exception):
    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg


class Syntax:
    def __init__(self, expression, col, condition, value):
        self.expression = expression
        self.col = col
        self.condition = condition
        self.value = value


def extract_value_from_equal(param_string):
    if "=" not in param_string:
        raise SensiSyntaxError("Incorrect syntax in param. Unable to find equal.")

    last_equal_position = param_string.rindex("=")
    syntax = param_string[:last_equal_position].strip('"')
    value = param_string[last_equal_position+1:]
    return syntax, value


def extract_target_column(param_string):
    param_string = param_string.strip('"')
    if ("[" in param_string) and (param_string.endswith("]")):
        right_quote_position = param_string.rindex("]")
        left_quote_position = param_string.rindex("[")
        syntax = param_string[:left_quote_position].strip('"')
        value = param_string[left_quote_position+1:right_quote_position]
        return syntax, value
    else:
        raise SensiSyntaxError("Incorrect syntax in param. Unable to find square quote at the end of syntax.")


def parse_param(input_syntax):
    syntax = None
    param_expression = ""
    param_col = ''
    param_condition = ''
    param_value = ''
    param_string = str(input_syntax).strip()

    if FILE_MARK not in input_syntax:
        param_string, param_value = extract_value_from_equal(input_syntax)
        return Syntax(param_string, param_col, param_condition, param_value)

    param_string, param_value = extract_value_from_equal(input_syntax)

    param_string = param_string[len(FILE_MARK):]
    # Checks if '.where' exists in param_string
    if ".where" in param_string:
        param_expression, param_condition = param_string.split(".where")
    else:
        param_expression = param_string

    # Gets the column in the para_expressions
    param_expression, param_col = extract_target_column(param_expression)
    param_names = re.findall(r'\[.+?\]', param_expression)

    result = "$"
    for name in param_names:
        result = "".join([result, "..*[@.name is '{}']".format(name.strip('[]'))])

    result = "".join([result, re.split(r'\[.+?\]', param_expression)[-1].strip('[]'), '.filename'])
    param_expression = result

    syntax = Syntax(param_expression, param_col, param_condition, param_value)
    return syntax


def query(data, expression):
    result = []
    if data and expression:
        if expression.startswith("$"):
            try:
                tree = Tree(data)
                result = tree.execute(expression)
                # If result is not a string (i.e. generator)
                # convert results to a list
                # In general: generators are returned when using an expression that contains ..* operator
                #             itertools can also be returned with just using .. operator
                if not isinstance(result, str):
                    result = list(result)

            except AttributeError as err:
                raise SensiSyntaxError("In Tree(data): ", err.message)

            except StopIteration:
                raise SensiSyntaxError("In tree.execute(expression): StopIteration")

            except SyntaxError:
                raise SensiSyntaxError("In tree.execute(expression): SyntaxError")

    elif data is None:
        raise SensiSyntaxError("Empty Data in query function")

    else:
        raise SensiSyntaxError("Empty Expression in query function")

    return result


def get_input_file_path(data, expression, env_dir):
    filename = query(data, expression)
    eco_name, driver_name = re.findall(r"(?<=')\w+(?=')", expression)
    driver_name = MODEL_DIR_NAMES[driver_name]

    if filename:
        eco_folder_id = query(data, "$.framework..*[@.name is '{}']".format(eco_name))
        if eco_folder_id:
            local_filepath = "/".join([eco_folder_id[0]['folder_id'], driver_name, filename[0]])
            # fetch root and input_root names from settings.json
            folder_id = query(data, "$.framework.sensi_1.folder_id")
            input_root_name = "RN_inputs" if query(data, "$.framework.name") == "RN" else "RW_inputs"
            file_path = os.path.join(env_dir, 'resources', folder_id, input_root_name, local_filepath).replace('\\', '/')
            if not os.path.exists(file_path):
                folder_name = query(data, "$.framework.sensi_1.name")
                file_path = os.path.join(env_dir, 'resources', folder_name, input_root_name, local_filepath).replace('\\', '/')
                if not os.path.exists(file_path):
                    raise SensiSyntaxError("Unable to find input file {}".format(file_path))

            return file_path

        else:
            raise SensiSyntaxError("Unable to find {} folder_id in settings.json".format(eco_name))
    else:
        raise SensiSyntaxError(f"Unable to find input file from expression {expression} in {env_dir}")


def get_selection_from_dataframe(selection, dataframe):
    if not dataframe.empty and selection.strip():
        col = selection.strip('[]')
        if col.count(',') == 1:
            column, row = col.split(',')
        elif col.count(',') == 0:
            column, row = col, None
        else:
            column, row = None, None

        if column:
            try:
                column = column.strip()
                if column.startswith("'") and column.endswith("'"):
                    dataframe = dataframe[[column.strip("'")]]
                elif column.count("'") == 0:
                    if column == "*":
                        pass
                    elif column.isnumeric():
                        if int(column) >= 1:
                            dataframe = dataframe[[dataframe.columns[int(column)-1]]]
                        else:
                            raise SensiSyntaxError("Unable to select because the {} column is less than 1".format(column))
                    else:
                        raise SensiSyntaxError("Unable to select because the {} column is not an int or *".format(column))
                else:
                    raise SensiSyntaxError("Unable to select because the {} column is not defined correctly".format(column))

            except KeyError:
                raise SensiSyntaxError("Unable to select because the {} column is not a valid column".format(column))

            except IndexError:
                raise SensiSyntaxError("Unable to select because the {} column is out of bounds".format(column))

        if row:
            try:
                row = row.strip()
                if row.startswith("'") and row.endswith("'"):
                    dataframe = dataframe.loc[[row.strip("'")]]
                elif row.count("'") == 0:
                    if row == "*":
                        pass
                    elif row.isnumeric():
                        if int(row) >= 1:
                            dataframe = dataframe.iloc[[int(row)-1], :]
                        else:
                            raise SensiSyntaxError("Unable to select because the {} row is less than 1".format(row))
                    else:
                        # TODO par Quincy: Throw error when incorrect column/row value
                        raise SensiSyntaxError("Unable to select because the {} row is not an int or *".format(row))
                else:
                    raise SensiSyntaxError("Unable to select because the {} row is not defined correctly".format(row))

            except KeyError:
                raise SensiSyntaxError("Unable to select because {} is not a valid row".format(row))

            except IndexError:
                raise SensiSyntaxError("Unable to select because the row {} is out of bounds".format(row))

    return dataframe


def select_from_dataframe(condition, operation, dataframe):
    lvalue, rvalue = condition.split(operation)
    if lvalue:
        lvalue = lvalue.strip()
        selected = get_selection_from_dataframe(lvalue, dataframe)
        if not selected.empty:
            if rvalue:
                values = rvalue.strip().split(',')
                for index in range(len(values)):
                    values[index] = values[index].strip()
                    if values[index]:
                        try:
                            values[index] = int(values[index])
                        except ValueError:
                            try:
                                values[index] = float(values[index])
                            except ValueError:
                                if values[index].lower() in ["true", "false"]:
                                    values[index] = values[index].lower() == "true"
                                else:
                                    pass

                if operation == "==":
                    dataframe = dataframe[selected.T.iloc[0].isin(values)]
                elif operation == "!=":
                    dataframe = dataframe[~selected.T.iloc[0].isin(values)]
                elif operation == ">=":
                    dataframe = dataframe[selected.T.iloc[0] >= values[0]]
                elif operation == ">":
                    dataframe = dataframe[selected.T.iloc[0] > values[0]]
                elif operation == "<=":
                    dataframe = dataframe[selected.T.iloc[0] <= values[0]]
                elif operation == "<":
                    dataframe = dataframe[selected.T.iloc[0] < values[0]]
                else:
                    raise SensiSyntaxError(" {} is an unsupported Operation!".format(operation))

                return dataframe

            else:
                raise SensiSyntaxError('No rvalue found in {}'.format(condition))

    else:
        raise SensiSyntaxError('No lvalue found in {}'.format(condition))


def interpret_condition(condition, dataframe):
    if condition.strip() and not dataframe.empty:
        condition = condition.strip()
        if condition.count('==') == 1:
            dataframe = select_from_dataframe(condition, "==", dataframe)
        elif condition.count('!=') == 1:
            dataframe = select_from_dataframe(condition, "!=", dataframe)
        elif condition.count('>=') == 1:
            dataframe = select_from_dataframe(condition, ">=", dataframe)
        elif condition.count('>') == 1:
            dataframe = select_from_dataframe(condition, ">", dataframe)
        elif condition.count('<=') == 1:
            dataframe = select_from_dataframe(condition, "<=", dataframe)
        elif condition.count('<') == 1:
            dataframe = select_from_dataframe(condition, "<", dataframe)
        else:
            raise SensiSyntaxError("{} is not a correct condition".format(condition))

    return dataframe


def apply_value_to_selection(value, selected_dict):
    operation = None

    value = value.strip()
    value = value.strip('"')
    cond1 = value.startswith("(") and value.endswith(")")
    cond2 = not value.startswith("(") and not value.endswith(")")
    if cond1 or cond2:
        value = value.strip("()")

    if value:
        if value[0] in ('+', '-', '*', '/'):
            operation, value = value[0], value.split(value[0])[1]
        if value:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    else:
                        pass

        if operation:
            if operation == '+':
                for column in selected_dict.keys():
                    selected_dict[column] = {k: v + value if not isinstance(value, (str)) and not isinstance(v, str) else value for k, v in selected_dict[column].items()}
            elif operation == '-':
                for column in selected_dict.keys():
                    selected_dict[column] = {k: v - value if not isinstance(value, (str)) and not isinstance(v, str) else -value for k, v in selected_dict[column].items()}
            elif operation == '*':
                for column in selected_dict.keys():
                    selected_dict[column] = {k: v * value if not isinstance(value, (str)) and not isinstance(v, str) else 0 for k, v in selected_dict[column].items()}
            elif operation == '/':
                for column in selected_dict.keys():
                    selected_dict[column] = {k: v / value if not isinstance(value, (str)) and not isinstance(v, str) else 0 for k, v in selected_dict[column].items()}
            else:
                raise SensiSyntaxError(" {} is an unsupported Operation!".format(operation))

        else:
            for column in selected_dict.keys():
                selected_dict[column] = {k: value for k, v in selected_dict[column].items()}

    return selected_dict


def apply_syntax_to_file(input_path, syntax, settings_json):
    # read path to dataframe
    # apply syntax
    if input_path and syntax and settings_json:
        seps = settings_json.get('gen_param').get('input_format')
        if seps:
            dec_sep = seps['dec_sep']
            col_sep = seps['col_sep']

            if os.path.exists(input_path):
                input_df = pd.read_csv(input_path, sep=col_sep)

                selected_df = None
                if syntax.condition:
                    # # print(syntax.condition)
                    condition = syntax.condition.strip('()')
                    or_conditions = condition.split('||')
                    df_or_list = []
                    for or_cond in or_conditions:
                        if or_cond.strip():
                            and_conditions = or_cond.split('&&')
                            df_and_list = []
                            for and_cond in and_conditions:
                                selected_df = interpret_condition(and_cond, input_df)
                                df_and_list.append(selected_df)

                            # TODO by Quincy: CHANGE merge to using conditions and selection with pandas
                            df_merge = df_and_list[0]
                            for df in df_and_list[1:]:
                                df_merge = pd.merge(df_merge, df, how='inner')
                            df_or_list.append(df_merge)

                    # print("Condition: ", syntax.condition, end=", ")
                    df_concat = pd.concat(df_or_list)

                if syntax.col:
                    # print(syntax.col)
                    try:
                        if syntax.condition:
                            selected_df = get_selection_from_dataframe(syntax.col, df_concat)
                        else:
                            selected_df = get_selection_from_dataframe(syntax.col, input_df)
                    except SensiSyntaxError as err:
                        index = err.msg.find("because")
                        final_msg = err.msg[:index] + 'from ' + input_path + ' ' + err.msg[index:]
                        raise SensiSyntaxError(final_msg)

                    # print("Column: ", syntax.col, end=" ")

                    # {"Nom_column": {"Num de ligne": "valeur associé"}}
                    selected_dict = selected_df.to_dict()
                    if syntax.value:
                        applied_dict = apply_value_to_selection(syntax.value, selected_dict)

                    # print("Value: ", syntax.value)
                    # # print(applied_dict)
                    # input_df = input_df.replace(applied_dict)

                    for column, indexes in applied_dict.items():
                        for index in indexes:
                            input_df.loc[index, column] = indexes[index]

                    # print(input_df)
                    os.remove(input_path)
                    input_df.to_csv(input_path, sep=col_sep, index=False)
                    return True
                else:
                    raise SensiSyntaxError("No col found for selection")
            else:
                raise SensiSyntaxError("Unable to find the input file {}".format(input_path))
        else:
            raise SensiSyntaxError("Unable to find the input_format in settings.json")
    else:
        msg = []
        if input_path is None:
            raise SensiSyntaxError("Unable to find input file to apply syntax")
        if syntax is None:
            raise SensiSyntaxError("No syntax to apply to file")
        if settings_json is None:
            raise SensiSyntaxError("Unable to read settings.json")

    return False

