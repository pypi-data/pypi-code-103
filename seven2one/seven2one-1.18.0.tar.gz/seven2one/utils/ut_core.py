
import json
import pytz
import os
import base64
import pandas as pd
from gql import gql
from dataclasses import dataclass
from tzlocal import get_localzone
from loguru import logger

if os.name == 'nt': #only if the platform is Windows, pyperclip will be imported
    import pyperclip

@dataclass
class Defaults:
    timeZone: str = "CET",
    dateTimeFormat: str = "dateTime"
    copyGraphQLString: bool = False

class Utils():

    def _timeZone(timeZone):
        if timeZone=='local': 
            localTimeZone = get_localzone().zone
            return str(pytz.timezone(localTimeZone))
        else:
            return str(pytz.timezone(timeZone))
    
    def _queryFields(fieldList:list, recursive=False):
        """
        Transforms a Python list of fields into graphQL String of fields
        including fields of referenced inventories        
        """
        fields = ''
        splitList = [item.split('.') for item in fieldList]
        logger.debug(f"Queried fields: {splitList}")

        def nestedItem(item):
            nonlocal fields
            line = ''
            for i in range(itemLength - 1):
                line += f'{item[i]} {{ '
            line += f'{item[-1]} '
            for _ in range(itemLength - 1):
                line += '}'
            line += ' \n'
            fields += line
    
        for item in splitList:
           
            if len(item) == 1:
                fields += f'{item[0]}  \n'
            else:
                itemLength = len(item)
                if recursive == False:
                    if item[-1] == '_displayValue':  
                        nestedItem(item)
                    if item[-1] == '_inventoryItemId':  
                        nestedItem(item)
                else:
                    nestedItem(item)
        return fields

    def _resolveFilter(whereString:str) -> str:
        """
        Resolves a simple where string into a GraphQL argument string
        """  
        EXECEPTION_STRING = f"""Filter syntax not correct - example syntax: 'colour eq "blue" and size gt "10"'"""

        ## Find quoted parts, both " and '
        positionList = []
        p = 0
        while p != -1:
            p = whereString.find('"', p + 1)
            if p != -1: positionList.append(p)
        if len(positionList) == 0:
            p = 0
            while p != -1:
                p = whereString.find("'", p + 1)
                if p != -1: positionList.append(p)
        if len(positionList) % 2 != 0:
            raise ValueError(EXECEPTION_STRING)
        if len(positionList) == 0:
            raise ValueError(EXECEPTION_STRING)
        for i, e in enumerate(positionList):
            if i % 2 != 0: 
                positionList[i] += 1

        ## Create a list of components
        positionList.insert(0, 0)
        positionList.append(positionList[-1])
        _components = []
        for i in range(len(positionList)):
            try:
                part = whereString[positionList[i] : positionList[i+1]]
                _components.append(part) 
            except: pass
        components = []
        for i, element in enumerate(_components):
            try:
                if i % 2 != 0:
                    components.append(element)
                else:
                    if element[0] == ' ':
                        element = element[1:]
                    if element[-1] == ' ':
                        element = element[:-1]
                    parts = element.split(' ')
                    for subElement in parts:
                        components.append(subElement)
            except: pass
            
        ## Clean list, replace ' by "    
        components = [i for i in components if i != '']
        components = [i.replace("'", '"') for i in components if i != '']
        
        ## Determine the correct numer of arguments where-criteroa may have
        correctArgLength = [x * 4 - 1 for x in range(1, 40)]
        
        ## Convert components list into GraphQL Filter String
        f = components
        if len(f) in correctArgLength :
            argNumber = int((len(f) + 1) / 4)

            argOpener = 'where: {\n'
            argFirst = f'{f[0]}: {{ {f[1]}: {f[2]} }}\n'
            argCloser = '}'
            argFollow = ''
            for i in range(1, argNumber):
                argFollow += f'{f[4*i-1]}: {{ {f[4*i]}: {{ {f[4*i+1]}: {f[4*i+2]} }} }}\n'
            
            return argOpener + argFirst + argFollow + argCloser
        else:
            raise ValueError(EXECEPTION_STRING)
    
    def _propertiesToString(properties:list) -> str:
        """ Converts a list of property dicts for many items into a string """
        
        _properties = '[\n'
        for property in properties:
            _properties += '{\n'
            for key, value in property.items():
                _properties += Utils._customProperties(key, value)      
            
            _properties += '}\n'
        _properties += ']'
        return _properties

    def _tsPropertiesToString(properties:list) -> str:
        """ Converts a list of property dicts for many items into a string """
        timeUnit, factor = 'timeUnit', 'factor'
        _properties = '[\n'
        for property in properties:
            _properties += '{\n'
            for key, value in property.items():
                if key == 'resolution':
                    try:
                        _properties += f'{key}: {{\n'
                        _properties += f'timeUnit: {value[timeUnit]}\n'
                        _properties += f'factor: {value[factor]}\n'
                        _properties += f'}}\n'
                    except KeyError:
                        logger.error("Missing 'timeUnit' and/or 'factor' for Timeseries resolution")
                        return
                else:
                    _properties += Utils._customProperties(key, value)
            
            _properties += '}\n'
        _properties += ']'
        return _properties

    def _addToGroupPropertiesToString(groupItemId:str, properties:list) -> str:
        """ Converts a list of property dicts for many items into a string """
        
        _properties = '[\n'
        for property in properties:
            _properties += f'{{_groupInventoryItemId: "{groupItemId}"\n'
            for key, value in property.items():
                _properties += Utils._customProperties(key, value)      
            
            _properties += '}\n'
        _properties += ']'
        return _properties

    def _uniquenessToString(propertyUniqueness: list):
        """ Converts a list of unique keys into a string """    

        _uniqueKeys = '[\n'
        for item in propertyUniqueness:
            key = item['uniqueKey']
            _uniqueKeys += f'{{uniqueKey: "{key}" properties: ['
            for value in item['properties']:
                _uniqueKeys += f'"{value}",'     
            
            _uniqueKeys += ']}\n'
        _uniqueKeys += ']'
        return _uniqueKeys

    def _customProperties(key:str, value:object) -> str:

        _propertyString = ''
        if key == 'dataType':
            _propertyString += f'{key}: {value}\n'
        elif type(value) == str:
            if len(value) >= 64 or '\n' in value or '"' in value:
                _propertyString += f'{key}: """{value}"""\n'
            else: 
                _propertyString += f'{key}: "{value}"\n'
        elif type(value) == int or type(value) == float:
            _propertyString += f'{key}: {value}\n'
        elif type(value) == bool:
            if value == True: _propertyString += f'{key}: true\n'
            if value == False: _propertyString += f'{key}: false\n'
        elif type(value) == list:
            _value = '['
            for element in value:
                if type(element) == int or type(element) == float:
                    _value += f'{element}, '
                elif type(element) == bool:
                    if element == True: element = 'true'
                    if element == False: element = 'false'
                    _value += f'{element}, '
                else:
                    _value += f'"{element}", '
            _propertyString += f'{key}: {_value}]\n'

        else:
            logger.error(f"{value} is an unsupported value type.")

        return _propertyString

    def _properties(self, inventoryName:str, recursive:bool=False) -> dict:
        """
        Returns a dictionary of properties and their types. 
        The function is used to create lists and flat dicts.
        """
        
        types = ['Boolean', 'String', 'DateTime', 'DateTimeOffset', 'Int', 'Long', 'Decimal', None]
        systemProperties = ['id', '_revision', '_propertyPermissions'] #'_inventoryItemId','_displayValue', 
        properties = {}
        _scheme = self.scheme['__schema']['types']

        def makeDict(dictName):
            subdict = {}
            nonlocal types, systemProperties, properties, _scheme
            for key in _scheme:
                if key['name'] == dictName:
                    for property in key['fields']:
                        if property['name'] not in systemProperties:
                            if property['type']['kind'] != 'OBJECT':
                                subdict.setdefault(property['name'], property['type']['name'])
                            else:
                                subdict.setdefault(property['name'], makeDict(property['type']['name']))
            logger.debug(f"Subdict: {subdict}")
            return subdict

        for key in _scheme:
            if key['name'] == inventoryName:
                for property in key['fields']:
                    if property['name'] not in systemProperties:
                        if property['type']['kind'] != 'OBJECT':
                            if property['type']['kind'] == 'LIST':
                                if property['type']['ofType']['kind'] == 'OBJECT':
                                    properties.setdefault(property['name'], {'_inventoryItemId': 'String'})
                                else:
                                    properties.setdefault(property['name'], property['type']['name'])
                            else:
                                properties.setdefault(property['name'], property['type']['name'])
                        else:
                            if recursive == True:
                                logger.debug("Recursive")
                                if property['type']['kind'] =='LIST':
                                    properties.setdefault(property['name'], {'_inventoryItemId': 'String'})
                                else:
                                    properties.setdefault(property['name'], makeDict(property['type']['name']))
                            else:
                                properties.setdefault(property['name'], property['type']['name'])
                
        logger.debug(f"Properties of inventory: {properties}")
        return properties

    def _propertyList(propertyDict:dict, recursive:bool=False) -> list:
        """Uses _properties() to create a flat list of properties"""

        propertyList = []
    
        def instDict(subDict, path):
            if recursive == True:
                for k, v in subDict.items():
                    if isinstance(v, dict):
                        path = f'{path}.{k}'
                        instDict(subDict[k], path)
                    else:
                        propertyList.append(f'{path}.{k}')
            else:
                if '_displayValue' in subDict.keys(): #if it is not an array
                    propertyList.append(f'{path}._displayValue')
                else: # if it is an array
                    propertyList.append(f'{path}._inventoryItemId')

        for k, v in propertyDict.items():
            if isinstance(v, dict):
                instDict(propertyDict[k], k)
            else:
                propertyList.append(k)

        logger.debug(f'Property list: {propertyList}')
        return propertyList
            
    def _propertyTypes(propertyDict:dict) -> dict:
        """Uses _properties() o create a flat dictionary of properties"""

        propertyTypes = {}
        
        def instDict(subDict, path):
            for k, v in subDict.items():
                if isinstance(v, dict):
                    path = f'{path}.{k}'
                    instDict(subDict[k], path)
                else:
                    propertyTypes.setdefault(f'{path}.{k}', v)

        for k, v in propertyDict.items():
            if isinstance(v, dict):
                instDict(propertyDict[k], k)
            else:
                propertyTypes.setdefault(k, v)

        return propertyTypes
        
    def _getDefaults() -> dict:
        """Returns all default values stored in config.json"""
        ## Check config file and create if not existing:
        path = os.path.abspath(__file__)
        path = path.replace('core.py', 'config.json')

        try:
            with open(path, 'r') as configFile:
                content = json.load(configFile)
        except:
            content = {
                'timeZone':'local',
                'dateTimeFormat':'dateTimeOffset',
                'copyGraphQLString': True
            }

        Defaults.copyGraphQLString = content['copyGraphQLString']
        Defaults.dateTimeFormat = content['dateTimeFormat']
        Defaults.timeZone = content['timeZone']
        return

    def _copyGraphQLString(graphQLString:str) -> None:
        """Can be applied to any core function to get the GraphQL string which is stored in the clipboard"""
        if Defaults.copyGraphQLString == True and os.name == 'nt':
           return pyperclip.copy(graphQLString)

    def _getVariantId(variants:pd.DataFrame, name:str) -> str:
        """ Gets the variant Id from a given name""" 
        variants.set_index('name', inplace=True)
        return variants.loc[name][0]

    def _getInventoryId(inventories:pd.DataFrame, name:str) -> str:
        """ Gets the variant Id from a given name""" 
        inventories.set_index('name', inplace=True)
        return inventories.loc[name][0]

    def _listGraphQlErrors(result:dict, key:str) -> None:
        """Print errors from GraphQL Query to log"""
        
        for i in result[key]['errors']:
            logger.error(i['message'])

    def _encodeBase64(file:str):
        with open(file) as file:
            content = file.read()
            content = base64.b64encode(content.encode('ascii'))
            return content.decode('UTF8')

    def _arrayItemsToString(arrayItems:list, operation:str, cascadeDelete:bool) -> str:
        """Converts a list of array items to a graphQL string"""

        cDelValue = 'true' if cascadeDelete == True else 'false'

        if operation == 'insert':
            _arrayItems = 'insert: [\n'
            for item in arrayItems:
                _arrayItems += f'{{value: "{item}"}}\n'
            _arrayItems += ']'
            return _arrayItems
        if operation == 'removeByIndex':
            _arrayItems = f'cascadeDelete: {cDelValue}\n'
            _arrayItems = 'removeByIndex: ['
            for item in arrayItems:
                _arrayItems += f'{item}, '
            _arrayItems += ']'
            return _arrayItems
        if operation == 'removeById':
            _arrayItems = f'cascadeDelete: {cDelValue}\n'
            _arrayItems = 'removeById: ['
            for item in arrayItems:
                _arrayItems += f'"{item}", '
            _arrayItems += ']'
            return _arrayItems

    def _executeGraphQL(self, graphQLString):
        """Executes GraphQl, this code is used in every main function"""

        Utils._copyGraphQLString(graphQLString)      
        logger.debug(f"GraphQLString: {graphQLString}")
        query= gql(graphQLString)

        try:
            result = self.client.execute(query)
        except Exception as err:
            logger.error(err)
            return
        
        return result