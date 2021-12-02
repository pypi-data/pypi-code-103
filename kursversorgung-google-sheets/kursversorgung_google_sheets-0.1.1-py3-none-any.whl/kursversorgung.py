"""
Created on 29.11.2021
This is a graphical user interface for the kursversorgung_functions.py file.
@author: baier
"""

from kursversorgung_google_sheets import *
from tkinter import *
import time
import datetime
import os

running = False  # Global flag
session = False  # Global flag


def main():

    def scanning():
        global running, session
        session = checkBloombergConnection()
        now = (datetime.datetime.now()).strftime('%d.%m.%Y %H:%M:%S')

        if session:  # Only do this if the Stop button has not been clicked
            if running:
                ticker = ws.col_values(1)[1:]
                ticker_pp = wsPP1.col_values(1)[1:]
                df = callBloombergApi(ticker, ticker_pp, fld1='Last_Price', fld2='Last_All_Sessions', fld3='Security_Name',
                                      fld4='EXCH_Market_Status', fld5='EQY_Split_Ratio', fld6='EQY_Split_DT')

                output.insert(END, updateLast(ticker, ticker_pp, df, now) + '\n')
                time.sleep(2.5)
                updateSecurityName(ticker, ticker_pp, df, now)
                time.sleep(2.5)
                updateWechselkurse(now)
                time.sleep(2.5)
                checkStatus(now)
        else:
            output.insert(END, f"{now}: Bloomberg connection could not be established!\n")

        root.after(900000, scanning)  # After 15 Minutes, call scanning again (create a recursive loop) 900000

    def start():
        """Enable scanning by setting the global flag to True."""
        global running, session
        running = True
        now = (datetime.datetime.now()).strftime('%d.%m.%Y %H:%M:%S')
        output.insert(END, f"{now}: Trying to establish connection to Bloomberg API.\n")

        session = checkBloombergConnection()

        if session:
            ticker = ws.col_values(1)[1:]
            ticker_pp = wsPP1.col_values(1)[1:]
            df = callBloombergApi(ticker, ticker_pp, fld1='Last_Price', fld2='Last_All_Sessions', fld3='Security_Name',
                                  fld4='EXCH_Market_Status', fld5='EQY_Split_Ratio', fld6='EQY_Split_DT')

            output.insert(END, f"{now}: Bloomberg connection established!\n\n")
            output.insert(END, updateLastSplits(ticker, df, now) + "\n")
            output.insert(END, updateLast(ticker, ticker_pp, df, now) + '\n')
        else:
            running = False
            output.insert(END, f"{now}: Bloomberg connection could not be established!\n")

    def stop():
        """Stop scanning by setting the global flag to False."""
        global running
        running = False
        now = (datetime.datetime.now()).strftime('%d.%m.%Y %H:%M:%S')
        output.insert(END, now + ": Updating has stopped\n")

    directory = os.path.dirname(__file__)
    root = Tk()
    root.title("Kursversorgung Warrants")
    root.geometry("620x400")
    root.iconbitmap(os.path.join(directory, 'software_update.ico'))

    app = Frame(root)
    app.grid()

    output = Text(root, height=12, width=73)
    start = Button(text="Start updating", command=start)
    stop = Button(text="Stop updating", command=stop)

    start.place(relx=0.5, rely=0.1, anchor=CENTER)
    stop.place(relx=0.5, rely=0.2, anchor=CENTER)
    output.place(relx=0.5, rely=0.5, anchor=CENTER)

    root.after(900000, scanning)  # After 15 Minutes, call scanning 900000
    root.mainloop()


if __name__ == '__main__':
    main()
