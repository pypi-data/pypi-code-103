'''from authenticate import create_client_with_scope
# from Kursversorgung import callBloombergApi
client = create_client_with_scope()

ws = client.open('KursversorgungWarrants').worksheet('Kurse')
wsPP1 = client.open('Private Placements').worksheet('Private Placements')

ticker = ws.col_values(1)[1:]
ticker_pp = wsPP1.col_values(1)[1:]'''

'''ticker = open(r"ticker_file.txt").read().splitlines()
tickerPP = open(r"ticker_pp_file.txt").read().splitlines()
print()

set_ticker = set(ticker)
set_tickerPP = set(tickerPP)
set_total = set.union(set_ticker, set_tickerPP)

print(len(ticker) + len(tickerPP), len(set_ticker), len(set_tickerPP))
print(len(set_total))
print(set_total)


textfile = open("ticker_file.txt", "w")
for element in ticker:
    textfile.write(element + "\n")
textfile.close()

textfile = open("ticker_pp_file.txt", "w")
for element in tickerPP:
    textfile.write(element + "\n")
textfile.close()
'''
'''from Kursversorgung import callBloombergApi, updateLastSplits, ws, updateSecurityName, updateLast, checkBloombergConnection
# ticker = open(r"ticker_file.txt").read().splitlines()
# ticker_pp = open(r"ticker_pp_file.txt").read().splitlines()
set_total = set.union(set(ticker), set(ticker_pp))

df = callBloombergApi(ticker, ticker_pp, fld1='Last_Price', fld2='Last_All_Sessions', fld3='Security_Name',
                      fld4='EXCH_Market_Status', fld5='EQY_Split_Ratio', fld6='EQY_Split_DT')

# updateLastSplits(ticker, df, '01.12.2021 08:32:00')
# updateSecurityName(ticker, ticker_pp, df, '01.12.2021 08:58:00')
# ws.update_cell(1, 21, '01.12.2021 08:58:00')
print(updateLast(ticker, ticker_pp, df, '01.12.2021 10:29:00'))
import pandas as pd
d = {'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]}
df = pd.DataFrame(data=d)

df = df[['col2', 'col3']]
print(df)'''
from kursversorgung_google_sheets import kursversorgung
