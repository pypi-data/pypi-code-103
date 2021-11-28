"""
Simple File Configuration Parse - by aaronater10
More info: https://github.com/aaronater10/sfcparse

Version 0.8.5

This module allows you to import and create custom python style save/config files for your program or script
on a plain text file. It can be used to export any data to a file as well. Also conains a feature for
easily formatting data types for clean multiline output when exporting data to files.

Importing [Python only]: returns a class with attributes from the file keeping python's natural recognition
of data types, including comments being ignored.

Exporting/Appending: it simply sends str data to a file. It may be used for any str data file output.

CleanFormat: simply formats any dict, list, set, or tuple to a clean multiline structure, and returned as str

Accepted Import Data Types: str, int, float, bool, list, dict, tuple, set, nonetype, bytes
"""
#########################################################################################################
# Imports
from ast import literal_eval as __literal_eval__
from typing import Any as __Any
from typing import Union as __Union


#########################################################################################################
# MODULE STARTS HERE

# Create hollow reference name for "class" to denote a class returned for hinting on imports
class __class:
    """Not meant to be used"""
    class Class:
        """Not meant to be used"""

# Import File Data
def importfile(filename: str) -> __class.Class:
    """
    Imports saved python data from any text file.

    Returns a class of attributes. Assign the output to var.

    Enter file location as str to import.

    Accepted data types: str, int, float, bool, list, dict, tuple, set, nonetype, bytes

    [Example Use]
    importfile('filename.test' or 'path\\to\\filename.test')
    """

    # Validate file exists. Open and Import Config File into Class Object then return the object    
    try:
        with open(filename, 'r') as f:
            f = f.read().splitlines()
    except FileNotFoundError:
        raise

    class file_data:

        # Syntax Error Message
        __py_syntax_err_msg = "importfile - Must have valid Python data types to import, or file is not formatted correctly"
        
        # Data Build Setup and Switches        
        __is_building_data_sw = False
        __body_build_data_sw = False
        __end_data_build_sw = False
        __build_data = ''

        # Markers
        __start_markers = {'[','{','('}
        __end_markers = {']','}',')'}
        __skip_markers = {'',' ','#','\n'}

        # Main File Loop
        for __file_data_line in f:

            # Set Skip Marker
            try:
                __skip_marker = __file_data_line[0]
            except:
                __skip_marker = ''

            # Skip Comments, Blank Lines, and potential New Lines
            if (__is_building_data_sw == False) and (__skip_marker in __skip_markers):
                continue

            # Set Syntax Check
            try:
                __syntax_check = __file_data_line.split()[1]
            except:
                __syntax_check = ''
            
            # Basic Syntax Check
            if (__syntax_check == '=') or (__is_building_data_sw):

                if not __is_building_data_sw:
                    __var_token = __file_data_line.split('=')[0].strip()
                    __value_token = __file_data_line.split('=')[1].strip()
                    __last_token = __file_data_line.split('=')[-1].strip()
            
                # START BUILD: Check if value in file line is only Start Marker. Check if Multline or Single Line
                if (__value_token in __start_markers) and (__last_token in __start_markers) and (__is_building_data_sw == False):
                    __build_data = __value_token
                    
                    # Turn ON Data Build Switches
                    __is_building_data_sw = True
                    __body_build_data_sw = True
                    __end_data_build_sw = True
                    continue
                
                # END BUILD: Check if line of file is an End Data Build Marker. Import Built Data Type if Valid
                elif (__end_data_build_sw) and (__file_data_line.strip() in __end_markers):
                    __build_data += __file_data_line

                    try: locals()[__var_token] = __literal_eval__(__build_data)
                    except: raise ValueError(__py_syntax_err_msg) from None

                    # Turn OFF Data Build Swiches
                    __is_building_data_sw = False
                    __body_build_data_sw = False
                    __end_data_build_sw = False
                    __build_data = ''
                    continue

                # CONT BUILD: Continue to Build Data
                elif __body_build_data_sw:
                    __build_data += __file_data_line
                    
                # IMPORT SINLGE LINE VALUES: If not multiline, assume single
                else:
                    try: locals()[__var_token] = __literal_eval__(__value_token)
                    except: raise ValueError(__py_syntax_err_msg) from None
            
            else: raise SyntaxError(__py_syntax_err_msg)

    # Return Final Import
    return file_data()


#########################################################################################################
# Export Data to File
def exportfile(filename: str, *data: __Any):
    """
    Exports a new file with the new data.
    
    Enter new filname as str, Pass any data type for output to file
    
    [Example Use]
    exportfile('filename.test' or 'path\\to\\filename.test', 'data1', 'data2')
    """

    # Export data to new file
    with open(filename, 'w') as f:
        for data_to_write in data:
            f.writelines(str(data_to_write))


#########################################################################################################
# Append Data to File
def appendfile(filename: str, *data: __Any):
    """
    Appends any data to a file.

    Enter existing filname as str, Pass any data type for output to file

    [Example Use]
    appendfile('filename.test' or 'path\\to\\filename.test', 'data1', 'data2')
    """

    # Append data to file
    try:
        with open(filename, 'r'):
            with open(filename, 'a') as f:
                for data_to_write in data:
                    f.writelines("\n" + str(data_to_write))            
    except FileNotFoundError:
        raise


#########################################################################################################
# Format/Prep Dictionary, List, Tuple, or Set Data for Export
def cleanformat(datatype: __Union[dict,list,tuple,set], indent_level: int=1) -> str:
    """
    Formats a (single) dictionary, list, tuple, or set, to have a clean multiline output for exporting to a file.

    Returned output will be a str.

    Note: Higher indent levels will decrease performance. Indentation is applied to the main data set only.

    Tip: Changing indent level to 0 increases cleaning performance by 5%, but output will have no indentation (Default = 1).

    Accepted data types: dict, list, tuple, set 

    [Example Use]
    var = cleanformat(datatype)
    """
    # Set indent level
    if not type(indent_level) == type(1):
        raise TypeError('cleanformat - Only int is allowed for indent level.')
    indent_level = '\t'*indent_level

    # Format Data Type and Return as str
    __build_data = ""

    # Dict
    if isinstance(datatype, dict):
        for key,value in datatype.items():
            __build_data += f"\n{indent_level}{repr(key)}: {repr(value)},"
        __build_data = f"{{{__build_data}\n}}"
        return __build_data

    # List
    elif isinstance(datatype, list):
        for value in datatype:
            __build_data += f"\n{indent_level}{repr(value)},"
        __build_data = f"[{__build_data}\n]"
        return __build_data

    # Tuple
    elif isinstance(datatype, tuple):
        for value in datatype:
            __build_data += f"\n{indent_level}{repr(value)},"
        __build_data = f"({__build_data}\n)"
        return __build_data

    # Set
    elif isinstance(datatype, set):
        for value in datatype:
            __build_data += f"\n{indent_level}{repr(value)},"
        __build_data = f"{{{__build_data}\n}}"
        return __build_data

    # Raise Error
    else:
        raise TypeError(
            """cleanformat - Only dict, list, tuple, or set are allowed.
           If tuple, it must be empty, have a single value with a "," [e.g. (1,)], or have >= 2 values
            """
        )