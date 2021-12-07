"""
Created on 02.07.2021
This is a program to monitor all the expiring values within the google sheet containing the Warrants
@author: baier
"""

import datetime
import pandas as pd
from accessOutlookEmail import create_account, send_email
from kursversorgung_google_sheets import createPrettyHTMLTable, create_client_with_scope

account = create_account('baier@orcacapital.de', 'Malfurion321')
client = create_client_with_scope()
ws = client.open('KursversorgungWarrants').worksheet('Kurse')


def getExpiringWarrants():
    ticker = ws.col_values(1)[1:]
    dateCol = ws.col_values(7)[1:]

    df = pd.DataFrame(list(zip(ticker, dateCol)), columns=['Ticker', 'Laufzeit'])
    today = datetime.date.today()
    timedelta = datetime.timedelta(31)
    endOfMonth = (today + timedelta).strftime('%Y-%m-%d')

    df.index += 2  # setz Index zu Zeilen in Excel
    df = df[df['Laufzeit'] != '']  # Filter auf alle Zeilen, die eine Laufzeit besitzen

    # sortiere DF nach der Laufzeit
    df['Laufzeit'] = pd.to_datetime(df['Laufzeit'], format='%d.%m.%Y')
    df = df[df['Laufzeit'] < endOfMonth]
    df = df.sort_values(by=['Laufzeit'])

    table = createPrettyHTMLTable(df)

    send_email(account, 'Auslaufende Warrants', table, ['dichtl@orcacapital.de', 'koenig@orcacapital.de',
                                                        'schroedl@orcacapital.de', 'grodon@orcacapital.de'])
    print('Monthly Report has been sent!')


def main():
    getExpiringWarrants()


if __name__ == '__main__':
    main()
