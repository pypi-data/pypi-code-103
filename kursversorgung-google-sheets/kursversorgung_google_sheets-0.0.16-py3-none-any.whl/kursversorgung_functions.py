"""
Created on 20.05.2021
This is a program to get all new Values for the provided Tickers in the Google Warrant Spreadsheet
@author: baier
"""
import pandas as pd
import blpapi
from accessOutlookEmail import create_account, send_email
from kursversorgung_google_sheets.authenticate import create_client_with_scope
from xbbg import blp

account = create_account('baier@orcacapital.de', 'Malfurion321')
recipients = ['schroedl@orcacapital.de', 'kreutmair@orcacapital.de']
client = create_client_with_scope()

ws = client.open('KursversorgungWarrants').worksheet('Kurse')
ws2 = client.open('KursversorgungWarrants').worksheet('Neue Warrants')
ws3 = client.open('KursversorgungWarrants').worksheet('Geschlossene Warrants')
ws4 = client.open('KursversorgungWarrants').worksheet('Währungstabelle')

wsPP1 = client.open('Private Placements').worksheet('Private Placements')
check = True


def checkBloombergConnection():
    options = blpapi.SessionOptions()
    options.setServerHost('localhost')
    options.setServerPort(8194)
    session = blpapi.Session(options).start()
    return session


def callBloombergApi(ticker_list_1: list, ticker_list_2: list, **kwargs):
    set_of_all_tickers = set.union(set(ticker_list_1), set(ticker_list_2)) # create a set of all the tickers
    list_of_all_tickers = list(set_of_all_tickers)
    ticker_with_equity = [f'{ticker.strip()} Equity' for ticker in list_of_all_tickers if ticker != '']

    if kwargs: df = blp.bdp(ticker_with_equity, list(kwargs.values()))
    else: return 'Please specify bloomberg fields you wanna request!'

    df.index = [item[:-7] for item in df.index.tolist()]
    return df


def parseStringToInteger(x):
    myList = []

    for s in x.split():
        if s[0] == '.':
            myList.append(float(s))
        if s.isdigit():
            myList.append(int(s))
        if s == 'for':
            continue

    # print(myList)
    value = (myList[0] / myList[1])
    return value


def logEntry(logfile_name: str, entry_type: str, timestamp: str, **kwargs):
    entry_data = kwargs.get('entry_data', None)
    logfile = open(rf"S:\Kursversorgung Warrents\{logfile_name}.txt", "a")
    new_entry = f'{timestamp} {entry_type}'
    if entry_data is not None:
        for fld in entry_data:
            new_entry = new_entry + ' ' + fld + ','
    logfile.writelines(new_entry)
    logfile.write('\n')


def updateDataType(celllist, check_pnl=False):
    if celllist[3].value == 'FALSE':
        celllist[3].value = False
    else:
        celllist[3].value = True
    if celllist[5].value:
        celllist[5].value = int(celllist[5].value.replace('.', ''))
    if celllist[7].value:
        celllist[7].value = float(celllist[7].value.replace(',', '.'))
    if celllist[8].value:
        celllist[8].value = float(celllist[8].value.replace(',', '.'))
    if celllist[9].value:
        celllist[9].value = float(celllist[9].value.replace(',', '.'))
    if celllist[10].value and check_pnl is False:
        celllist[10].value = int(celllist[10].value.replace('.', ''))
    else:
        celllist[10].value = None
    if celllist[11].value and check_pnl is False:
        celllist[11].value = float((celllist[11].value.replace('%', '')).replace(",", '.')) / 100
    else:
        celllist[11].value = None


def checkStatus(timestamp: str):
    # checke das Kurs-Sheet, ob blanke Warrants drin stehen und verkaufte/geschlossene
    kurse_status = ws.col_values(14)[1:]
    reviewed = ws2.col_values(20)[1:]
    reversed_warrants = ws3.col_values(14)[1:]

    max_rows_new = (len(ws.get_all_values()))
    max_rows_closed = (len(ws3.get_all_values()))
    # For-Loop für geschlossene, verfallene, ausgeübt Warrants        --- VON 1 NACH 3
    for i, item in enumerate(reversed(kurse_status)):
        y = len(kurse_status) + 1 - i
        if item != 'Offen':
            if item == '':
                ws.update_cell(y, 14, 'Offen')
                kurse_status[y - 2] = 'Offen'
            else:
                row_values = ws.row_values(y)
                celllistWS1 = ws.range('A' + str(y) + ':S' + str(y))
                updateDataType(celllistWS1)

                ws3.append_row(['placeholder1'])
                max_rows_closed += 1

                celllistWS3 = ws3.range('A' + str(max_rows_closed) + ':S' + str(max_rows_closed))
                for j, inhalt in enumerate(celllistWS3): inhalt.value = celllistWS1[j].value
                ws3.update_cells(celllistWS3)

                ws.delete_rows(y)
                max_rows_new -= 1

                # insert entry to logfile
                logEntry('LOGFILE', 'ADD to Geschlossene Warrants from Kurse ->', timestamp, entry_data=row_values)

    # For-Loop für Neue Warrants                                      --- VON 2 NACH 1
    for i, item in enumerate(reversed(reviewed)):
        y = len(reviewed) + 1 - i

        if item == 'Eingebucht':
            row_values = ws2.row_values(y)[:-1]
            celllistWS2 = ws2.range('A' + str(y) + ':S' + str(y))
            updateDataType(celllistWS2, True)

            ws.append_row(['placeholder2'])
            max_rows_new += 1

            celllistWS1 = ws.range('A' + str(max_rows_new) + ':S' + str(max_rows_new))
            for j, inhalt in enumerate(celllistWS1): inhalt.value = celllistWS2[j].value
            ws.update_cells(celllistWS1)

            ws2.delete_rows(y)

            # insert entry to logfile
            logEntry('LOGFILE', 'ADD to Kurse from Neue Warrants ->', timestamp, entry_data=row_values)

    # For-Loop für geschlossene Warrants, die wieder geöffnet wurden    --- VON 3 NACH 1
    for i, item in enumerate(reversed(reversed_warrants)):
        y = len(reversed_warrants) + 1 - i

        if item == 'Offen':
            row_values = ws3.row_values(y)

            celllistWS3 = ws3.range('A' + str(y) + ':S' + str(y))
            updateDataType(celllistWS3, True)

            ws.append_row(['placeholder3'])
            max_rows_new += 1

            celllistWS1 = ws.range('A' + str(max_rows_new) + ':S' + str(max_rows_new))
            for j, inhalt in enumerate(celllistWS1): inhalt.value = celllistWS3[j].value
            ws.update_cells(celllistWS1)

            ws3.delete_rows(y)
            max_rows_closed -= 1

            # insert entry to logfile
            logEntry('LOGFILE', 'ADD to Kurse from Geschlossene Warrants ->', timestamp, entry_data=row_values)


def updateWechselkurse(timestamp: str):
    bloombergTicker = ws4.col_values(5)[2:]
    df = blp.bdp(bloombergTicker, ['last_price'])
    kurse = [df.loc[item].at['last_price'] for item in bloombergTicker]

    cell_list = ws4.range('D3:D' + str(len(kurse) + 2))
    for i, val in enumerate(kurse): cell_list[i].value = val

    ws4.update_cells(cell_list)
    ws4.update_cell(1, 7, timestamp)


def updateLast(ticker: list, ticker_pp: list, df: pd.DataFrame, timestamp: str):
    # Update Last in Kursversorgung Warrants
    df = df.fillna({'last_price': 0, 'last_all_sessions': 0})
    # create a Dict for all currencies
    # boerse = ws4.col_values(1)[1:]
    # wechselkurse = ws4.col_values(4)[1:]
    # währungsdict = {}
    # for i, item in enumerate(boerse):
    #    boerse[i] = ' ' + item
    # währungsdict = dict(zip(boerse, wechselkurse))

    # Kursversorgung Warrants Sheet
    priceList = []  # iterate over all tickers, if price is pulled from Bloomberg, add to list, if not add 0
    for item in ticker:
        boersenkuerzel = item[-3:]
        if boersenkuerzel in item and len(boersenkuerzel) == 3:
            # kurs = währungsdict.get(boersenkuerzel)
            # kurs = float(kurs.replace(",", "."))
            try:
                newPrice = df.loc[item].at['last_price']
                if boersenkuerzel == ' US': newPrice = df.loc[item].at['last_all_sessions']
                priceList.append(round(newPrice, 4))
            except (ValueError, KeyError, OSError) as err:
                logEntry('LOGFILE', f'{err} threw an exception', timestamp)
                priceList.append(0)
        else: priceList.append(0)

    cell_list = ws.range('I2:I' + str(len(ticker) + 1))  # insert CELLRANGE into Google worksheet
    for i, val in enumerate(priceList): cell_list[i].value = val  # Update Values in CellList

    # Update Last in Private Placements
    priceList1 = []
    for item in ticker_pp:
        try:
            newPrice = df.loc[item].at['last_price']
            priceList1.append(round(newPrice, 4))
        except (ValueError, KeyError, OSError) as err:
            logEntry('LOGFILE_PP', f'{err} threw an exception', timestamp)
            priceList1.append(0)

    cell_list1 = wsPP1.range('I2:I' + str(len(ticker_pp) + 1))
    for i, val in enumerate(priceList1): cell_list1[i].value = val

    try:
        ws.update_cells(cell_list)
        wsPP1.update_cells(cell_list1)
        ws.update_cell(1, 21, timestamp)
        wsPP1.update_cell(1, 24, timestamp)
        return f'{timestamp}: Last Price was updated correctly'
    except (ValueError, KeyError, OSError) as err:
        return f'{err} was raised in updateLast()'


def updateSecurityName(ticker: list, ticker_pp: list, df: pd.DataFrame, timestamp: str):
    # Update Security Name in Kursversorgung Warrants
    beschreibung = ws.col_values(2)[1:]
    df_tkch = df[df['exch_market_status'] == 'TKCH']
    del df_tkch['security_name']

    for i, item in enumerate(ticker):
        global check
        try:
            if item in df_tkch.index and item != 'TICKER CHANGE':
                ws.update_cell(str(i + 2), 2, 'TICKER CHANGE')
                log_data = f'TICKER CHANGE Index: {str(i + 2)} = {beschreibung[i]}'
                logEntry('LOGFILE', log_data, timestamp)
                send_email(account, 'Ticker Change Kursversorgung Warrants', log_data, recipients)
                check = False
                continue
            sec_name = df.loc[item].at['security_name']
            if sec_name != beschreibung[i] and check is True:
                try:
                    ws.update_cell(str(i + 2), 2, sec_name)
                    logEntry('LOGFILE', f'NAMECHANGE Index: {str(i + 2)} = {beschreibung[i]} TO {sec_name} in Kurse',
                             timestamp)
                except (ValueError, KeyError, OSError) as err:
                    logEntry('LOGFILE', f'{err} was raised', timestamp)
        except (ValueError, KeyError, OSError) as err:
            logEntry('LOGFILE', f'{err} was raised', timestamp)

    # Update Security Name in Private Placements
    beschreibung = wsPP1.col_values(2)[1:]

    for i, item in enumerate(ticker_pp):
        check = True
        try:
            if item in df_tkch.index and item != 'TICKER CHANGE':
                wsPP1.update_cell(str(i + 2), 2, 'TICKER CHANGE')
                log_data = f'TICKER CHANGE Index: {str(i + 2)} = {beschreibung[i]}'
                logEntry('LOGFILE_PP', log_data, timestamp)
                send_email(account, 'Ticker Change Private Placements', log_data, recipients)
                check = False
                continue
            sec_name = df.loc[item].at['security_name']
            if sec_name != beschreibung[i] and check is True:
                try:
                    wsPP1.update_cell(str(i + 2), 2, sec_name)
                    logEntry('LOGFILE_PP', f'NAMECHANGE Index: {str(i + 2)} = {beschreibung[i]} TO {sec_name} in Kurse',
                             timestamp)
                except (ValueError, KeyError, OSError) as err:
                    logEntry('LOGFILE_PP', f'{err} was raised', timestamp)
        except (ValueError, KeyError, OSError) as err:
            logEntry('LOGFILE_PP', f'{err} was raised', timestamp)


def updateLastSplits(ticker: list, df: pd.DataFrame, timestamp: str):
    pd.options.mode.chained_assignment = None  # default='warn'
    df = df[['eqy_split_ratio', 'eqy_split_dt']].dropna()

    df['eqy_split_dt'] = pd.to_datetime(df['eqy_split_dt'], format='%Y-%m-%d')
    df['eqy_split_dt'] = df['eqy_split_dt'].map(lambda x: x.strftime('%d.%m.%Y'))
    df['eqy_split_ratio'] = df['eqy_split_ratio'].map(lambda x: parseStringToInteger(x))

    cell_listDate = ws.range('P2:P' + str(len(ticker) + 1))
    cell_listRatio = ws.range('Q2:Q' + str(len(ticker) + 1))

    for i, item in enumerate(ticker):  # check if Ticker is in the modified DF, which only contains EQYs with Splits
        if item not in df.index:
            cell_listRatio[i].value = None
            cell_listDate[i].value = None
        else:  # Set the Cell Value to the new found Split
            if cell_listDate[i].value != df.loc[item].at['eqy_split_dt']:
                cell_listRatio[i].value = df.loc[item].at['eqy_split_ratio']
                cell_listDate[i].value = df.loc[item].at['eqy_split_dt']
                log_data = f'SPLIT Index: {str(i + 2)} = {item}'
                logEntry('LOGFILE', log_data, timestamp)  # Log every Split, which was insert
                send_email(account, 'Split in Kursversorgung Warrants', log_data, recipients)

    ws.update_cells(cell_listDate)  # Update Cell Lists in GoogleSheet
    ws.update_cells(cell_listRatio)
    return f"{timestamp}: Program has updated Last Splits for all Equities"
