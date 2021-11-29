from __future__ import print_function
from __future__ import absolute_import

from optparse import OptionParser, Values

import os
import platform as plat
import sys
import blpapi
from numpy import inner
import pandas as pd
import datetime


class BloombergClient():

    def __init__(self):

        self.session = self.start_session()
        self.refDataService = self.open_service(self.session, "//blp/refdata")
    
    def start_session(self):

        options = parseCmdLine()

        # Fill SessionOptions
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost(options.host)
        sessionOptions.setServerPort(options.port)

        # Create a Session
        session = blpapi.Session(sessionOptions)

        # Start a Session
        if not session.start():
            raise Exception
        return session
    
    def open_service(self, session, service):

        if not session.openService(service):
            raise Exception

        # Obtain previously opened service
        refDataService = session.getService(service)
        return refDataService

    def process_messages(self, message_type, single):

        messages = []
        while(True): 
            ev = self.session.nextEvent(500)
            for msg in ev:
                if str(msg.messageType()) == message_type:
                    if single:
                        if message_type == "ReferenceDataResponse":
                            return msg.getElement("securityData").getValueAsElement(0).getElement("fieldData")
                        elif message_type == "HistoricalDataResponse":
                            return msg.getElement("securityData").getElement("fieldData")
                    else:
                        messages.append(msg)
                    
            if ev.eventType() == blpapi.Event.RESPONSE:
                break
        return messages
    

    def earnings_dates(self, tickers):

        earnings_dates = {ticker : [] for ticker in tickers}
        tickers = [ticker + " US Equity" for ticker in tickers]
        
        request = self.refDataService.createRequest("ReferenceDataRequest")
        for ticker in tickers:
            request.append("securities", ticker)
        request.append("fields","ERN_ANN_DT_AND_PER")
        session.sendRequest(request)
        while(True):
            # We provide timeout to give the chance for Ctrl+C handling:
            ev = session.nextEvent(500)
            for msg in ev:
                el = msg.asElement()
                if el.name() == "ReferenceDataResponse":
                    c = el.getChoice()                   
                    for ticker_data in c.values():
                        ticker = ticker_data.getElementValue("security").replace(" US Equity","")
                        for dp in ticker_data.getElement("fieldData").getElement("ERN_ANN_DT_AND_PER").values():                            
                            if "Q" in dp.getElementValue("Earnings Year and Period"):
                                try:
                                    earnings_dates[ticker].append(dp.getElementValue("Earnings Announcement Date"))
                                except:
                                    pass
            if ev.eventType() == blpapi.Event.RESPONSE:
                # Response completly received, so we could exit
                break
        session.stop()
        return earnings_dates
    
    
    def get_estimate(self, ticker, field, quarters_back):
        
        request = self.refDataService.createRequest("ReferenceDataRequest")
        request.append("securities", ticker + " US Equity")
        request.append("fields", field)
        if quarters_back > -1:
            overrides = request.getElement("overrides")
            override1 = overrides.appendElement()
            override1.setElement("fieldId","BEST_FPERIOD_OVERRIDE")
            override1.setElement("value","-{q}FQ".format(q=quarters_back))
        self.session.sendRequest(request)
        try:
            message = self.process_messages("ReferenceDataResponse", True)
            return message.getElementValue(field)
        except:
            return None  
    def get_earnings_dates(self, ticker):

        ed = []
        request = self.refDataService.createRequest("ReferenceDataRequest")
        request.append("securities", ticker + " US Equity")
        request.append("fields", "ERN_ANN_DT_AND_PER")
        self.session.sendRequest(request)
        message = self.process_messages("ReferenceDataResponse", True)
        for period in message.getElement("ERN_ANN_DT_AND_PER").values():
            if "Q" in period.getElementValue("Earnings Year and Period"):
                try:
                    ed.append(period.getElementValue("Earnings Announcement Date"))
                except:
                    pass
        return ed

    def get_reporting_field(self, ticker, field):

        request = self.refDataService.createRequest("HistoricalDataRequest")
        request.append("securities",ticker + " US Equity")
        request.append("fields", field)
        request.set("startDate", "20180101")
        request.set("endDate", datetime.datetime.today().strftime("%Y%m%d"))
        self.session.sendRequest(request)
        message = self.process_messages("HistoricalDataResponse", True)
        return {period.getElementValue("date") : period.getElementValue(field) for period in message.values()}


    def get_quarterly_financials(self, tickers):

        reporting_fields = ["SALES_REV_TURN","GROSS_PROFIT","ARD_GROSS_PROFITS","IS_EPS", "IS_COMP_EPS_ADJUSTED", "IS_BASIC_EPS_CONT_OPS", "ARD_ADJUSTED_EPS","IS_ADJUSTED_EPS_AS_REPORTED"]
        estimate_fields = ["BEST_SALES","BEST_EPS"]
        multipliers = {"SALES_REV_TURN":1000000, "GROSS_PROFIT":1000000, "ARD_GROSS_PROFITS":1000000, "BEST_SALES":1000000}
        reporting_df = pd.DataFrame()
        reported = {ticker : {field : {} for field in reporting_fields} for ticker in tickers}
        earnings_dates = {ticker : [] for ticker in tickers}
        
        #get reporting data 
        for ticker in tickers:
            periods = {}
            for field in reporting_fields:
                values = self.get_reporting_field(ticker, field)
                for date, val in values.items():
                    try:
                        periods[date][field] = val
                    except:
                        periods[date] = {field: val, "date":date, "symbol":ticker}
            for period in periods.values():
                reporting_df = reporting_df.append(period, ignore_index=True)

        #get earnings report dates
        for ticker in tickers:
            earnings_dates[ticker] = self.get_earnings_dates(ticker)
        reporting_df["ann_date"] = reporting_df.apply(lambda x: choose_announcement_date(x["date"], earnings_dates[x["symbol"]]), axis=1)
        
        ticker_dfs = []
        #get estimates
        for ticker in tickers:
            sdf = reporting_df[reporting_df["symbol"] == ticker].copy().sort_values("date", ascending=False)
            for field in estimate_fields:
                estimates = []
                for i in range(len(sdf)):
                    estimates.append(self.get_estimate(ticker, field, i))
                sdf[field] = estimates
            ticker_dfs.append(sdf)
        df = pd.concat(ticker_dfs)
        for field, multiplier in multipliers.items():
            if field in df.columns:
                df[field] = df[field] * multiplier
        return df
        

def parseCmdLine():
    parser = OptionParser(description="Retrieve reference data.")
    parser.add_option("-a",
                      "--ip",
                      dest="host",
                      help="server name or IP (default: %default)",
                      metavar="ipAddress",
                      default="localhost")
    parser.add_option("-p",
                      dest="port",
                      type="int",
                      help="server port (default: %default)",
                      metavar="tcpPort",
                      default=8194)

    (options, args) = parser.parse_args()

    return options


def choose_estimate(ann_date, estimates):

    estimate_dates = list(estimates.keys())
    estimate_dates = [x for x in estimate_dates if x < ann_date]
    estimate_dates.sort()
    if len(estimate_dates) == 0:
        return None
    return estimates[estimate_dates[-1]]


def choose_announcement_date(data_date, ann_dates):

    possible_dates = [x for x in ann_dates if x > data_date]
    possible_dates.sort()
    return possible_dates[0]