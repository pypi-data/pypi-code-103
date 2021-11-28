import logging
logger = logging.getLogger('smartypes')
from datetime import datetime






def checkStr(xstr,testFloat=False):
    # checck what type are possible for a str input
    #TODO make it with learning for a given field or field group will first test the types in the best order 
    dateformats=['%Y-%m-%d','%d/%m/%Y %H:%M:%S','%d-%m-%Y %H:%M:%S','%d-%m-%Y','%d/%m/%Y']
    if type(xstr) is str :
        if testFloat:
            try :
                xval = float(xstr)
                logger.debug(f'float {xval} ')
                return xval
            except :
                logger.debug(f'not float {xval} ')
        for df in dateformats:
            try :
                xval=datetime.strptime(xstr,df)
                logger.debug(f'date {xval} ')
                return xval
            except :
                logger.debug(f'date format {df} not working')
        return xstr
    else :
        return xstr

