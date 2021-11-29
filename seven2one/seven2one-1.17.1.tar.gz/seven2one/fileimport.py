import csv
import sys

from loguru import logger

from time import sleep
from pprint import pprint

from .utils.ut_fileimport import FileUtils
#from .core import TechStack
from . import core, timeseries
#TechStack = core.TechStack

class FileImport(FileUtils):

    def __init__(self, core, timeSeries=None):
        global tsClient, coreClient
        coreClient = core
        #self.client = client
        if timeSeries != None:        
            tsClient = timeSeries       

    def importNewInventory(self, filePath:str, delimiter:str):
        """
        Creates a new inventory from a CSV file
        
        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str
            The CSV delimiter. Choose ',', ';', or 'tab'.

        Example:
        --------
        >>> createInventoryFromCsv(filePath='C:\\temp\\CreateMeterData.csv', delimiter=';')          
        """

        with open(filePath) as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file] 

         ## CHECK FILE
        if content[0][0] != 'name':
            logger.error(f"Wrong format. Expected header 'name' (for inventory) at position (0, 0).")
            return
        if content[2][0] != 'name':
            logger.error(f"Wrong format. Expected header 'name' (for property) at position (2, 0).")
            return

        inventoryName = content[1][0]

        if not inventoryName: 
            logger.error("Inventory name missing")
            return

        ## PREPARE IMPORT
        propertyList =[]   
        boolKeys = ['nullable', 'isArray', 'isReference'] 
        keys = [item for item in content[2]]
        columns = len(keys)

        for i, row in enumerate(content):
            if i >= 3:
                propertyDict = {}
                for column in range(columns):
                    if content[2][column] in boolKeys:
                        if row[column] == 'false': value = False
                        if row[column] == 'true': value = True
                    elif not row[column]: continue
                    else: value = row[column]
                    propertyDict.setdefault(content[2][column], value)
                propertyList.append(propertyDict)

        ## IMPORT
        logger.debug(propertyList)
        result = core.TechStack.createInventory(self, inventoryName, propertyList)
        if result == {'createInventory': {'errors': None}}: 
            logger.info(f"Inventory {inventoryName} created.")

    def importBasicItems(self, filePath:str, delimiter:str, inventoryName:str,
        chunkSize:int = 500, pause:int = 1) -> None:
        """
        Imports basic inventory items from a CSV file. The CSV file only needs a header of
        property definitions. Each line below the header represents a new basic item.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str
            The CSV delimiter. Choose ',', ';', or 'tab'.
        inventoryName : str
            The field name of the inventory.
        chunkSize : int
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 500 items per chunk.
        pause : int
            Between each chunk upload a pause is inserted in order to avoid overloading.
            Default is 1 second.

        Example:
        --------
        >>> importBasicItems(filePath='C:\\temp\\BasicItems.csv', delimiter=';'
            inventoryName='meterData')          
        """
        # start = time()
        # if timeZone == None:
        #     timeZone = core._getDefaults()['timeZone']
               
        ## READ FILE
        with open(filePath) as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file]   

        ## PREPARE IMPORT   
        properties = core.TechStack.inventoryProperties(coreClient, inventoryName)
        logger.debug(f'Property names: {list(properties["name"])}')

        diff = FileUtils._comparePropertiesBasic(properties, content[0])
        if len(diff) > 0:
            print(f"Unknown properties: {list(diff)}")
            return

        dataType, isArray, nullable = FileUtils._analyzeProperties(inventoryName, properties)
        logger.debug(f'Data types: {dataType}')
        logger.debug(f'Array properties: {isArray}')
        logger.debug(f'Nullable properties: {nullable}')
        logger.info(f"File '{filePath}' read and properties analyzed")

        basicItems = FileUtils._createBasicItems(content, dataType, isArray, nullable)
        logger.debug(f'Basic items: {basicItems}' )


        # ## IMPORT
        if len(basicItems) > chunkSize:
            lenResult = 0
            for i in range(0, len(basicItems), chunkSize):
                result = core.TechStack.addBasicItems(coreClient, inventoryName, basicItems[i : i + chunkSize])
                logger.info(f"{len(result)+lenResult} items of {len(basicItems)} imported. Waiting {pause} second(s) before continuing...")
                sleep(pause)
        else:
            result = core.TechStack.addBasicItems(coreClient, inventoryName, basicItems)
            logger.info(f"{len(result)} basic items of file '{filePath}' imported.")

        return

    def importTimeSeriesItems(self, filePath:str, delimiter:str, inventoryName:str,
        chunkSize:int = 50, pause:int = 1) -> None:
        """
        Imports time series inventory items from a CSV file. The CSV file only needs a header of
        property definitions. Each line below the header represents a new time series.

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str
            The CSV delimiter. Choose ',', ';', or 'tab'.
        inventoryName : str
            The field name of the inventory.
        chunkSize : int
            Determines the number of items which are written per chunk. Using chunks
            can be necessary to avoid overloading. Default is 50 items per chunk.
        pause : int
            Between each chunk upload a pause is inserted in order to avoid overloading.
            Default is 1 second.

        Example:
        --------
        >>> importTimeSeriesItems(filePath='C:\\temp\\TimeSeriesItems.csv', delimiter=';'
            inventoryName='meterData')          
        """

        # if timeZone == None:
        #     timeZone = core._getDefaults()['timeZone']
               
        ## READ FILE
        with open(filePath) as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file]   

        ## PREPARE IMPORT
        tsProperties = ['unit', 'timeUnit', 'factor']
        for header in tsProperties:
            if not header in content[0]:
                logger.error(f"Header {header} not found. Import aborted.")
                return 
           
        properties = core.TechStack.inventoryProperties(coreClient, inventoryName)
        logger.debug(f'Property names: {list(properties["name"])}')

        diff = FileUtils._comparePropertiesTimeSeries(properties, content[0])
        if len(diff) > 0:
            print(f"Unknown properties: {list(diff)}")
            return

        dataType, isArray, nullable = FileUtils._analyzeProperties(inventoryName, properties)
        logger.debug(f'Data types: {dataType}')
        logger.debug(f'Array properties: {isArray}')
        logger.debug(f'Nullable properties: {nullable}')
        logger.info(f"File '{filePath}' read and properties analyzed")

        timeSeriesItems = FileUtils._createTimeSeriesItems(content, dataType, isArray, nullable)
        logger.debug(f'Time series items: {timeSeriesItems}' )


        # ## IMPORT
        if len(timeSeriesItems) > chunkSize:
            lenResult = 0
            for i in range(0, len(timeSeriesItems), chunkSize):
                result = timeseries.TimeSeries.addTimeSeriesItems(tsClient, inventoryName, timeSeriesItems[i : i + chunkSize])
                logger.info(f"{len(result)+lenResult} items of {len(timeSeriesItems)} imported. Waiting {pause} second(s) before continuing...")
                sleep(pause)
        else:
            result = timeseries.TimeSeries.addTimeSeriesItems(tsClient, inventoryName, timeSeriesItems)
            logger.info(f"{len(result)} items of {len(timeSeriesItems)} imported.") 
        return

    def importTimeSeriesData(self, filePath:str, delimiter:str, inventoryName:str) -> None: 
        """
        Imports Time Series data from a CSV file with a timestamp column as 
        first column and inventoryItemIds for the first row. Time Series values are 
        spanned as matrix of both axes. 

        Parameters:
        -----------
        filePath : str
            The file path of the csv file that should be imported.
        delimiter : str
            The CSV delimiter. Choose ',', ';', or 'tab'.
        inventoryName : str
            The field name of the inventory.
        timeZone : str
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone.

        Example:
        --------
        >>> importTimeSeriesData(filePath='C:\\temp\\TsData.csv', delimiter=';'
            inventoryName='meterData', timeZone='Asia/Tokyo')
        -------
        """
    
        ## READ FILE
        with open(filePath) as f:
            csv_file = csv.reader(f, delimiter=delimiter)
            content = [row for row in csv_file]

        ## VERIFY IDS, CREATE DATA_DICTS, IMPORT
        for column in range(1, len(content[0])):
            inventoryItemId = content[0][column]
            properties = core.TechStack.items(coreClient, inventoryName, fields=['unit', 'resolution'], filter=f'_inventoryItemId eq "{inventoryItemId}"')
            if properties.empty:
                logger.error(f"Unknown Time Series with inventoryItemId {inventoryItemId}")
                continue

            properties['resolution.factor'] = properties['resolution'].str.partition(' ')[0]
            properties['resolution.timeUnit'] = properties['resolution'].str.partition(' ')[2]

            valueDict = {}
            for i, row in enumerate(content):
                if i >= 1:
                    try:
                        float(row[column])
                        valueDict.setdefault(row[0], row[column])
                    except:
                        logger.warning(f"No valid value {row[column]} in {row[0]} of {inventoryItemId}.")
                        continue
                    
            timeseries.TimeSeries.setTimeSeriesData(
                self=tsClient,
                inventoryName=inventoryName,
                inventoryItemId=inventoryItemId, 
                timeUnit=properties.loc[0, 'resolution.timeUnit'],
                factor=properties.loc[0, 'resolution.factor'],
                unit=properties.loc[0, 'unit'],
                dataPoints=valueDict
                )
                    
            logger.info(f'Imported {len(valueDict)} values for Time Series {inventoryItemId}')

        logger.info(f"Import finished")
        return