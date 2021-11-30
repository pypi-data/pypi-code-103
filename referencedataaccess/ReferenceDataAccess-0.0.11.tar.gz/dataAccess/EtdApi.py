# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 10:44:00 2020

@author: Sangoi
"""

import requests
import json
from rduaccess.EquityApi import EquityApi
import pandas as pd
from rduaccess.EtdUtil import convert_json_to_df


class EtdApi(object):
    """
    This class hold all methods to access etd (derivatives - futures/options/strategies) data
      
    """

    def __init__(self, key, base_url='https://sfbrekezl8.execute-api.eu-west-2.amazonaws.com/FreeTrial/'):
        """ 
        Initialize the class
        Keyword Arguments:
            key:  RDUAccess api key

        """

        self.key = key
        self.base_url = base_url
        self.all_column_list = ["exchCd", "lstngCycleTp", "omic", "segTp", "smic", "tckSz", "tckVal", "trdStsTp",
                                "vndrExchCd", "ticker", "bbgIdBBGlobal", "rduSecId", "rduSegId",
                                "bbgCompositeIdBbGlobal", "rduSecIdExp", "rduSegIdExp", "gmiFullPrdCd", "name",
                                "roundLotSz", "clrngCd", "name", "roundLotSz", "trdCtyCd", "trdCcyMajorFl", "trdCcyCd",
                                "dayNum", "maxOrdSz", "tckSzDnmntr", "prdTp", "flexElgblFl", "clrngCcyCd",
                                "msrmntUntCd", "tckSzNmrtr", "spotMnthPosLmt", "mnthPosLmt", "allMnthPosLmt",
                                "blckTrdElgblFl", "actFl", "exchCd", "wkNum", "exchRptngLvl", "cftcRptngLvl",
                                "trdStsTp", "cftcRegFl", "undlRltnsTp", "clrngCd", "rduPrdId", "name", "assetTp",
                                "expDt", "lstTrdDt", "settleDt", "frstDlvryDt", "frstNtcDt", "lstDlvryDt", "name",
                                "vndrAssetTp", "prntAssetTp", "strikePx", "cfi", "yrCd", "settleTp", "ctrSz",
                                "frstTrdDt", "settleFixDt", "numOfLegs", "accrlStrtDt", "accrlEndDt", "mnthCd",
                                "dayNum", "pntVal", "flexFl", "actFl", "wkNum", "lstNtcDt", "trdStsTp", "cfiCd", "isin",
                                "bbgTicker", "bbgIdBbUnique", "aiiCode", "ric", "trAssetId", "trQuoteId", "ricRoot",
                                "ult_under_name", "ult_under_ric", "ult_under_ticker", "ult_under_isin",
                                "ult_under_rduSecId", "exchPrfx", "immed_under_name", "immed_under_ric",
                                "immed_under_ticker", "immed_under_isin", "immed_under_rduSecId"]


    """
    This method calls the resp api.
    """

    def __call_api(self, query, url):
        headers = {'x-api-key': self.key, 'accept': 'application/json'}
        response = requests.get(url, params=query, headers=headers)
        data = response.text
        if not data:
            data = "{\"message\":\"No Data Found\"}"
        json_data = json.loads(data)
        return json_data

    def get_by_isin_with_underlier_data(self, isin, columnList=[]):
        """
        
        This will return the etd data given the isin
        Parameters
        ----------
        isin : String
            The ISIN code.
        columnList : List    
            Specify the list of column's that needs to be returned in output. 
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with isin " + isin)
        query = {'isin': isin}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/standard/getByIsin')

        if not columnList:
            columnList.extend(self.all_column_list)

        data = convert_json_to_df(self.key, isin, json_data, fetchUnderlying=True, columnList=columnList)
        columnList = []
        return data

    def get_by_isin(self, isin, columnList=[]):
        """
        
        This will return the etd data given the isin
        Parameters
        ----------
        isin : String
            The ISIN code.
        columnList : List    
            Specify the list of column's that needs to be returned in output. 
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with isin " + isin)
        query = {'isin': isin}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/standard/getByIsin')

        if not columnList:
            columnList.extend(self.all_column_list)

        data = convert_json_to_df(self.key, isin, json_data, fetchUnderlying=False, columnList=columnList)

        columnList = []
        return data

    def get_by_isins(self, isins=[], columnList=[]):
        """
        This will return the etd data given the isins
        Keyword Arguments:

        Parameters
        ----------
        isins : TYPE, optional
            DESCRIPTION. The default is [].

        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.

        """
        data = []
        for isin in isins:
            t_data = self.get_by_isin(isin, columnList)
            data.append(t_data)
        data = pd.concat(data)
        return data

    def get_by_ticker_with_underlier_data(self, ticker, exchangeCode, columnList=[]):
        """
        This will return the etd data given the ticker and echange code
       

        Parameters
        ----------
        ticker : String
            Exchange symbol (also known as Ticker or Trade Symbol) of contract.
        exchangeCode : String
            Exchange code of the session where the security is trading.

        Returns
        -------
        data : dataframe
            This will return a dataframe with key as ticker+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.

        """
        print("Calling get_by_exchange_symbol with isin " + ticker + " exchangeCode-" + exchangeCode)
        query = {'ticker': ticker, 'exchangeCode': exchangeCode}
        json_data = self.__call_api(query, self.base_url + 'etd/standard/getByExchangeSymbol')
        if not columnList:
            columnList.extend(self.all_column_list)

        data = convert_json_to_df(self.key, ticker, json_data, fetchUnderlying=True)

        return data

    def get_by_ticker(self, ticker, exchangeCode, columnList=[]):
        """
        This will return the etd data given the ticker and echange code
       

        Parameters
        ----------
        ticker : String
            Exchange symbol (also known as Ticker or Trade Symbol) of contract.
        exchangeCode : String
            Exchange code of the session where the security is trading.

        Returns
        -------
        data : dataframe
            This will return a dataframe with key as ticker+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.

        """
        print("Calling get_by_exchange_symbol with isin " + ticker + " exchangeCode-" + exchangeCode)
        query = {'ticker': ticker, 'exchangeCode': exchangeCode}
        json_data = self.__call_api(query, self.base_url + 'etd/standard/getByExchangeSymbol')
        if not columnList:
            columnList.extend(self.all_column_list)

        data = convert_json_to_df(self.key, ticker, json_data, fetchUnderlying=False)

        return data

    def get_output_attributes_doc(self):
        """
        The output of all the function supported returns 
        """
        df = pd.read_csv("column_document.csv")

        return df
