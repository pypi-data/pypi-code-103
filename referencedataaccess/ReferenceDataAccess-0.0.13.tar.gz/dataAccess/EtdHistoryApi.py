# -*- coding: utf-8 -*-
"""
Created on Tues Nov 30 21:46:15 2021

@author: Sangoi
"""

import requests
import json

import pandas as pd
from dataAccess.EtdUtil import convert_json_to_df


class EtdHistoryApi(object):
    """
    This class hold all methods to access etd (derivatives - futures/options/strategies) historical data

    """

    def __init__(self, key, base_url='https://stsqzppv1j.execute-api.eu-west-2.amazonaws.com/FreeTrial/'):
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

    def get_by_isin(self, isin, dt, column_list=[]):
        """

        This will return the etd data given the isin
        Parameters
        ----------
        isin : String
            The ISIN code.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)
        column_list : List
            Specify the list of column's that needs to be returned in output.
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with isin " + isin)
        query = {'isin': isin, 'dt': dt}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/history/standard/getByIsin')

        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, isin, json_data, fetchUnderlying=False, columnList=column_list)

        column_list = []
        return data

    def get_by_isins(self, isins, dt, column_list=[]):
        """
        This will return the etd data given the isins
        Keyword Arguments:

        Parameters
        ----------
        isins : TYPE, optional
            DESCRIPTION. The default is [].
        dt : date on which the data needs to be fetched (format is YYYYMMDD)

        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.

        """
        data = []
        for isin in isins:
            t_data = self.get_by_isin(isin, dt, column_list)
            data.append(t_data)
        data = pd.concat(data)
        return data

    def get_by_ticker(self, ticker, exchange_code, dt, column_list=[]):
        """
        This will return the etd data given the ticker and exchange_code


        Parameters
        ----------
        ticker : String
            Exchange symbol (also known as Ticker or Trade Symbol) of contract.
        exchange_code : String
            Exchange code of the session where the security is trading.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)

        Returns
        -------
        data : dataframe
            This will return a dataframe with key as ticker+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.

        """
        print("Calling get_by_exchange_symbol with isin " + ticker + " exchangeCode-" + exchange_code)
        query = {'ticker': ticker, 'exchangeCode': exchange_code, 'dt': dt}
        json_data = self.__call_api(query, self.base_url + 'etd/history/standard/getByExchangeSymbol')
        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, ticker, json_data,  fetchUnderlying=False, columnList=column_list)

        return data

    def get_by_ric(self, ric, dt, column_list=[]):
        """

        This will return the etd data given the isin
        Parameters
        ----------
        ric : String
            Reuter's identifier.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)
        column_list : List
            Specify the list of column's that needs to be returned in output.
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByIsin with ric " + ric)
        query = {'ric': ric, 'dt': dt}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/history/standard/getByRic')

        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, ric, json_data, fetchUnderlying=False, columnList=column_list)

        column_list = []
        return data

    def get_by_occ_symbol(self, occ_symbol, dt, column_list=[]):
        """

        This will return the etd data given the isin
        Parameters
        ----------
        occ_sumbol : String
            Reuter's identifier.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)
        column_list : List
            Specify the list of column's that needs to be returned in output.
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByOccSym with occ_symbol " + occ_symbol)
        query = {'occSym': occ_symbol, 'dt': dt}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/history/standard/getByOccSym')

        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, occ_symbol, json_data, fetchUnderlying=False, columnList=column_list)

        column_list = []
        return data

    def get_by_bbg_ticker(self, bbg_ticker, dt, column_list=[]):
        """

        This will return the etd data given the isin
        Parameters
        ----------
        bbg_ticker : String
            Bloomberg's ticker.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)
        column_list : List
            Specify the list of column's that needs to be returned in output.
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByBbgTicker with bbg_ticker " + bbg_ticker)
        query = {'bbgTicker': bbg_ticker, 'dt': dt}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/history/standard/getByBbgTicker')

        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, bbg_ticker, json_data, fetchUnderlying=False, columnList=column_list)

        column_list = []
        return data

    def get_by_bbg_idb_global(self, bbg_idb_global, dt, column_list=[]):
        """

        This will return the etd data given the isin
        Parameters
        ----------
        bbg_idb_global : String
            Bloomberg's Idb global identifier.
        dt : date on which the data needs to be fetched (format is YYYYMMDD)
        column_list : List
            Specify the list of column's that needs to be returned in output.
            If no column's are specified, then it will return all the columns
        Returns
        -------
        data : dataframe
            this will return a dataframe with key as isin+exchange.
            To get description on the columns of dataframe, call get_output_attributes_doc.
        """
        print("Calling getByBbgIdBbGlobal with bbg_ticker " + bbg_idb_global)
        query = {'bbgIdBbGlobal': bbg_idb_global, 'dt': dt}
        json_data = self.__call_api(query,
                                    self.base_url + 'etd/history/standard/getByBbgIdBbGlobal')

        if not column_list:
            column_list.extend(self.all_column_list)

        data = convert_json_to_df(self.key, bbg_idb_global, json_data, fetchUnderlying=False, columnList=column_list)

        column_list = []
        return data
