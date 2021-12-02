"""
Created on 02.07.2021
This is a program to monitor all the expiring values within the google sheet containing the Warrants
@author: baier
"""

from pretty_html_table import build_table
import pandas as pd
from accessOutlookEmail import create_account, send_email
from bs4 import BeautifulSoup as bS
from kursversorgung_google_sheets import create_client_with_scope

account = create_account('baier@orcacapital.de', 'Malfurion321')
client = create_client_with_scope()
ws = client.open('KursversorgungWarrants').worksheet('Kurse')


def createPrettyHTMLTable(df):
    indexList = df.index.to_list()

    warrantsDF = pd.DataFrame(columns=['Ticker', 'Beschreibung', 'Anmerkung', 'Restricted', 'Closing', 'Anzahl',
                                       'Laufzeit', 'Strike', 'Last', 'AK', 'PnL', 'PnL in %', 'Broker', 'Status',
                                       'Pricing Underlaying', 'Last Split', 'Split Ratio', 'Zuletzt bearbeitet am',
                                       'Bearbeiter'])
    for idx in indexList:
        to_append = ws.row_values(idx)
        a_series = pd.Series(to_append, index=warrantsDF.columns)
        warrantsDF = warrantsDF.append(a_series, ignore_index=True)

    pretty_html = build_table(warrantsDF, 'blue_light')
    soup = bS(pretty_html, 'lxml')
    table = soup.find_all('table')[0]

    for row in table.find_all('tr'):
        col_marker = 0
        col_marker2 = 0
        cols = row.find_all('td')
        value_list = [x.text.strip() for x in cols]

        for value in value_list:
            if col_marker2 == 10:
                try:
                    value = int(value.replace('.', ''))
                    value = float((value.replace('%', '')).replace(',', '.'))
                except AttributeError: pass

                for col in cols:
                    if col_marker in [10, 11]:
                        if value < 0: col['style'] += '; color: red'
                        elif value > 0: col['style'] += '; color: green'
                    col_marker += 1
            col_marker2 += 1

    return table


def getDailyPnL():
    ticker = ws.col_values(1)[1:]
    pnlabsolut = ws.col_values(11)[1:]
    pnlinpercent = ws.col_values(12)[1:]

    df = pd.DataFrame(list(zip(ticker, pnlabsolut, pnlinpercent)), columns=['Ticker', 'PnL', 'PnL in %'])
    df.index += 2  # setz Index zu Zeilen in Excel

    # edit PnL in %
    df = df[df['PnL in %'] != '0,00%']
    df = df[~df['PnL in %'].str.contains("-", na=False)]
    df['PnL in %'] = df['PnL in %'].str.replace(',', '.').str.replace('%', '')
    df['PnL in %'] = pd.to_numeric(df['PnL in %'])
    df = df[df['PnL in %'] > 30]  # filter by value bigger than 30 percent

    # edit PNL
    df['PnL'] = df['PnL'].str.replace('.', '', regex=True)
    df['PnL'] = pd.to_numeric(df['PnL'])
    df = df[df['PnL'] > 20000]  # filter by value bigger than 20.000
    df = df.sort_values(by=['PnL in %'], ascending=False)

    table = createPrettyHTMLTable(df)

    send_email(account, 'Daily Warrant Report', table, ['dichtl@orcacapital.de', 'grodon@orcacapital.de',
                                                        'koenig@orcacapital.de'])


def main():
    getDailyPnL()


if __name__ == '__main__':
    main()
