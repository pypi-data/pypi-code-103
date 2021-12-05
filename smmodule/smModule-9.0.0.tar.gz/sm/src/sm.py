__encoding__ = "utf-8"
__license__ = "CopyRight and Idea by Pascal Vallaster - all rights reserved"
__os__ = "Originally based on Linux-Distribution | later improved on Windows 10 Distribution"
__help__ = """Help - sm.py:
Parameters:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helpmenu:              [-h][--help]
Encoding:              [--encoding][-e]
License:               [-l][--license]
OS:                    [-os][--os]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains all kinds of stuff.
From database-/xml- and json-engine
up to math-tools, general stuff, colors
for strings and copy-paste-section.
Read more in the README.md"""


import os
import sys
import time
import json
import _sqlite3
import platform
import datetime
# import itertools
# from threading import Thread
from smtplib import SMTP
from fractions import Fraction
from colorama import init, Fore, Style
import xml.etree.ElementTree as ElementTree

#####################################################################

"""
    -----------------------------------------------------------------
    General - Stuff:
    -----------------------------------------------------------------
"""


def check_system():
    if "Windows" in platform.platform():
        return "Windows"
    else:
        return "Unix"


def quit():
    sys.exit()


def clear():
    if check_system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def sleep(sec: int):
    time.sleep(sec)


def check_input_int():
    # This function checks, if the users input(entry = input(": ")) is a integer.
    while True:
        entry = input(": ")
        try:
            entry = int(entry)
            return entry
        except ValueError:
            print("This is not a correct entry. Try it again!")


def makeString(_list: list, filling: str = "") -> str:
    string = ""
    for element in _list:
        string += element + filling
    return string


#####################################################################

"""
    -----------------------------------------------------------------
    Math - Stuff:
    -----------------------------------------------------------------
"""


def fracture(counter: int = 1, denominator: int = 1, p: bool = False):
    if denominator == 0:
        print("\x1B[31mValueError:\x1B[0m")
        print("\x1B[31mDenominator have to be upper than 0!\x1B[0m")
        # raise ZeroDivisionError("Error: got for denominator 0 -- denominator shout != 0")
    else:
        frac = Fraction(counter, denominator)
        if p:
            print(str(frac))

        return frac


def check_int(nZ, p: bool = True):
    # This function checks, if nZ is a integer.
    try:
        nZ = float(nZ)
        if p:
            print(str(nZ))
        return True
    except ValueError:
        return False


def N(nZ, p: bool = True):
    # This function checks, if nZ is part of natural numbers.
    if nZ > -1:
        if p:
            print(str(nZ))
        return True
    else:
        return False


def Nu(nZ, p: bool = True, ):
    # This function checks, if nZ is part of natural uneven numbers.
    if nZ % 2 != 0:
        if p:
            print(str(nZ))
        return True
    else:
        return False


def Ne(nZ, p: bool = True):
    # This function checks, if nZ is part of even numbers.
    if nZ % 2 == 0:
        if p:
            print(str(nZ))
        return True
    else:
        pass


def P(nZ, p: bool = True):
    # This function checks, if nZ is part of prime numbers
    prim = True
    if nZ == 1:
        prim = False
    else:
        i = 2
        while i <= nZ - 1:
            if nZ % i == 0:
                prim = False
            i += 1
    if prim:
        if p:
            print(str(nZ))
        return True
    else:
        return False


#####################################################################

"""
    -----------------------------------------------------------------
    Hacking - Stuff:
    -----------------------------------------------------------------
"""


def attack(bssid: str, interf: str):
    # This function attack the chosen wifi.
    # Attention: This function needs Bssid and interface!
    print("How many Deauth.Commands shout this attack run against the wifi?")
    deauth = input("Deauth.Commands: ")
    os.system("aireplay-ng --deauth " + deauth + " -a " + bssid + " " + interf)


#####################################################################

"""
    -----------------------------------------------------------------
    DB - Stuff: 
    -----------------------------------------------------------------
"""


def HowTo():
    print("""
General use of sql-commands:
####
-Add elements to column:
    INSERT INTO table(columnname, columname, ...) VALUES('value', 'value', ...)
-Get elements from column in table:
    SELECT columnname FROM table WHERE condition
    for row in run_command.fetchall():
        Result_Command.append(str(row))     or row[0] 1, 5, 9, 55, ... 
-Get all elements from column in table:
    SELECT columnname FROM table
-Get all elements from all column in table:
    SELECT * from table
-Delete elements in columns:
    DELETE FROM table WHERE condition
-Update elements in table:
    UPDATE table SET columnname = 'sample' WHERE condition
-Get last entry of colum(s):
    SELECT max(colum(s)) FROM table
####

This example showes, how to read out a column in a SQLite DB:
Example How To use dbworker:
####
    class dbreader(dbworker):
        db_path = "/user/home/testDB"
        result = []

        def run_sql(self, sqlcom="SELECT Titel FROM Books"):
            self.c.execute(sqlcom)
            self.connection.commit()
            for row in self.c.fetchall():
                self.result.append(str(row))
                print(self.result)

    dbreader().run_sql()
####""")


class IncorrectEntry(Exception):
    pass


class dbworker:
    """
    This is the class dbworker. In here, you can execute SQL-statement ore use the predefined functions, such as INSERT,SELECT...
    If you use the predefined functions and your entry is None or just "", its raises an IncorrectEntry-ERROR.
    You can simply catch this error with:
    
    import sm.IncorrectEntry as IE
    
    try:
        SELECT_ELEMENTs(table="", column="cloumn1", condition="column1='text'")
    except IE:
        print("Incorrect Entry!")

    :exception IncorrectEntry
    """

    # Path to db-file to open
    db_path = ""

    def __init__(self):
        self.connection = _sqlite3.connect(self.db_path, check_same_thread=False)
        self.c = self.connection.cursor()
        self.output = ""

    def close(self):
        self.connection.close()

    def run_sqlCommand(self, sqlcom: str):
        self.c.execute(sqlcom)
        self.connection.commit()

    def check_vars(self, *args: str):
        if args[1] == "":
            raise IncorrectEntry("\nIncorrect entry for variable: '" + args[0] + "'\nGot 'NONE' instead") from None

    def INSERT(self, table: str, column: str, value: str, condition: str = ""):
        """
        This function is for inserting one or more values into a column of a table.
        It could be very tricy to use, because you have to thread the values very special(showen in Sample)

        Sample:

        INSERT(table="test", column="column1, column2, column3", '"value1", "value2", "value3"', condition="column1='text'")

        :param table:
        :param column:
        :param value:
        :param condition:
        :return:
        """
        self.check_vars("table", table)
        self.check_vars("column", column)
        self.check_vars("value", value)
        sqlcom = 'INSERT INTO ' + table + '(' + column + ') VALUES(' + value + ')'
        if condition != "":
            sqlcom += " WHERE " + condition
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c

    def SELECT_ELEMETs(self, table: str, column: str, condition: str = ""):
        """
        This function is for selecting elements in a table from one of more columns.

        Sample:

        SELECT_ELEMENTs(table="test", column="column1", condition="column1='text'")

        :param table:
        :param column:
        :param condition:
        :return:
        """
        self.check_vars("table", table)
        self.check_vars("column", column)
        sqlcom = "SELECT " + column + " FROM " + table
        if condition != "":
            sqlcom += " WHERE " + condition
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c

    def SELECT_ALL(self, table: str, condition: str = ""):
        """
        This functions is for selecting all elements in a table.

        Sample:

        SELECT_ALL(table="test", condition="column1='text'")

        :param table:
        :param condition:
        :return:
        """
        self.check_vars("table", table)
        sqlcom = "SELECT * FROM " + table
        if condition != "":
            sqlcom += " WHERE " + condition
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c

    def DELETE(self, table: str, condition: str = ""):
        """
        This function is for deleting tables and/or columns in a database.

        Sample:

        DELETE(table="test")

        DELETE(table="test", condition="column1='text'")

        :param table:
        :param condition:
        :return:
        """
        self.check_vars("table", table)
        sqlcom = "DELETE FROM " + table
        if condition != "":
            sqlcom += " WHERE " + condition
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c

    def UPDATE(self, table: str, column: str, value: str, condition: str = ""):
        """
        This functions is for updating one ore more columns.

        Sample:

        UPDATE(table="test", column="column1", value="new_text")
        UPDATE(table="test", column="column1", value="new_text", condition="column1='text'")

        :param table:
        :param column:
        :param value:
        :param condition:
        :return:
        """
        self.check_vars("table", table)
        self.check_vars("column", column)
        sqlcom = 'UPDATE ' + table + ' SET ' + column + ' = "' + value + '"'
        if condition != "":
            sqlcom += " WHERE " + condition
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c

    def getLastEntry(self, table: str, column: str = ""):
        """
        This function is for getting the last entry of a column in a table.

        Sample:

        getLastEntry(table="test", column="column1")

        :param table:
        :param column:
        :return:
        """
        self.check_vars("table", table)
        self.check_vars("column", column)
        sqlcom = "SELECT max(" + column + ") FROM " + table
        self.c.execute(sqlcom)
        self.connection.commit()
        self.output = self.c


#####################################################################

"""
    -----------------------------------------------------------------
    XML Stuff: 
    -----------------------------------------------------------------
"""


class XMLworker:
    """
    This is the class XMLworker. In here, you can work with xml files (tags, texts, ...)
    !Important!
    Your XML-File must contain a root class

    Usage Example:

    from sm import XMLworker
    class xml(XMLworker)
        XML_path = "PathToXML-File"

        def __init__(self):
            super(xml, self).__init__()

        def change_text():
            image_tag = self.XMLroot[0]
            image_tag.text = "NewPathName"

    instance = xml()
    instance.change_text()
    instance.overwrite()

    """
    XML_path = ""

    def __init__(self):
        self.xml_file_parse = ElementTree.parse(self.XML_path)  # To handle the file itself
        self.XMLroot = self.xml_file_parse.getroot()  # To interact with the xml file/content

    def overwrite(self, file_path=XML_path):
        # Overwrites the file after changing it, otherwise tha file wont be saved
        self.xml_file_parse.write(file_path)

    def insert_element(self, tag: str):
        # Inserts a new tag into the xml file
        tag = ElementTree.Element(tag)
        self.XMLroot.insert(1, tag)


#####################################################################

"""
    -----------------------------------------------------------------
    JSON Stuff: 
    -----------------------------------------------------------------
"""


class JSONworker:
    """
    This is the class JSONworker. In here, you can work with json files

    Usage Example:

    from sm import JSONworker
    class JSON(JSONworker)
        json_path = "PathToJSON-File"

        def __init__(self):
            super(JSON, self).__init__()



    instance = JSON()
    instance.data['test_var'] = "test_value"
    instance.write(data=self.data)
    """
    json_path = ""

    def __init__(self):
        with open(self.json_path) as file:
            self.data = json.load(file)  # Data: to interact/change... the JSON-File

    def write(self, data, indent: int = 4):
        # (Over-) Writes the JSON-File with the new content (self.)data
        data_to_write = json.dumps(data, indent=indent)
        with open(self.json_path, "w") as file:
            file.write(data_to_write)


#####################################################################

"""
    -----------------------------------------------------------------
    Mail Stuff: 
    -----------------------------------------------------------------
"""


def send_mail(sender, password, name, receiver, subject, msg_text):
    debuglevel = 0

    smtp = SMTP("smtp.gmail.com", 587)
    smtp.set_debuglevel(debuglevel)
    # smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, password)

    from_addr = f"{name} <{sender}>"
    to_addr = receiver
    # subj = "Verification - Key"
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" \
          % (from_addr, to_addr, subject, date, msg_text)

    smtp.sendmail(from_addr, to_addr, msg)
    smtp.quit()


#####################################################################


"""
    -----------------------------------------------------------------
    Log Stuff: 
    -----------------------------------------------------------------
"""


class logMaker:
    """
    This is the class logMaker. In here, you can create and write a log
    """
    file_path = ""
    mode = ""

    def __init__(self, assume_old_content: bool = True):
        data = ""
        if assume_old_content:
            if os.path.isfile(self.file_path):
                with open(self.file_path, f"r{self.mode}") as f:
                    data = f.read()
        self.file = open(self.file_path, f"w{self.mode}")
        if data:
            self.file.write(data + "\n")

    def writeLog(self, log: [str, bytes], strftime:str="%d/%m/%Y, %H:%M:%S"):
        if type(log) is bytes:
            strftime = bytes(datetime.datetime.now().strftime(strftime))
        else:
            strftime = str(datetime.datetime.now().strftime(strftime))
        self.file.write(strftime + " - " + log + "\n")
        self.file.flush()

    def close(self):
        self.file.close()


#####################################################################


"""
    -----------------------------------------------------------------
    Color Stuff (to use colors for str):
    -----------------------------------------------------------------
"""


class colors:
    init()

    RED = Fore.RED
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    BLACK = Fore.BLACK
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    MAGENTA = Fore.MAGENTA

    RESET = Fore.RESET
    BRIGHT = Style.BRIGHT
    NORMAL = Style.NORMAL


#####################################################################


"""
    -----------------------------------------------------------------
    Animations, LoadingSymbols:
    -----------------------------------------------------------------
"""


def point_animation(text: str, t: int = 1, d: int = 2, loading_text: str = "..."):
    if d <= 1:
        raise ValueError("Parameter 'd' is less or equal 1! Parameter d has to be more or equal 1!")
    run_counter = 1
    while run_counter <= d:
        while_counter = 0
        while while_counter < len(loading_text):
            sys.stdout.write("\r" + text + loading_text[:while_counter])
            sys.stdout.flush()
            while_counter += 1
            time.sleep(t)
        run_counter += 1


def stick_animation(text: str, t: int = 0.15, d: int = 2, loading_text: str = "|/-\\"):
    table2 = list("abcdefghijklmnopqrstuvwxyzöäüß")
    table1 = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜß")
    if d <= 1:
        raise ValueError("Parameter 'd' is less or equal 1! Parameter d has to be more or equal 2!")
    text = text.lower()
    list_text = list(text)
    loading_counter = 0
    # dynamik_text = ""
    run_counter = 1
    while run_counter <= d:
        while_counter = 0
        while while_counter < len(list_text):
            dynamik_text = ""
            if list_text[while_counter] in table2:
                for_counter = 0
                for letter in table2:
                    if letter == list_text[while_counter]:
                        list_text[while_counter] = table1[for_counter]
                        break
                    else:
                        pass
                    for_counter += 1
                for letter in list_text:
                    dynamik_text += letter
                dynamik_text += "  " + loading_text[loading_counter]
                sys.stdout.write("\r" + dynamik_text)
                sys.stdout.flush()
                time.sleep(t)
                list_text[while_counter] = table2[for_counter]
                loading_counter += 1
                if loading_counter == 4:
                    loading_counter = 0
            while_counter += 1
        run_counter += 1


#####################################################################
"""
    -----------------------------------------------------------------
    Copy-Paste Code:
    -----------------------------------------------------------------
"""

"""
import strings
def wordlist(wordl_min=1, wordl_max=10):
    word_kind = string.ascii_letters  # string.lowercase   string.uppercase    string.digits    string.punctuation
    for i in range(wordl_min, wordl_max):
        for j in map(''.join, itertools.product(word_kind, repeat=3)):
            gen_words = j"""

#####################################################################

"""
    -----------------------------------------------------------------
    Main Stuff:
    -----------------------------------------------------------------
"""

if __name__ == "__main__":
    if "--encoding" in sys.argv or "-e" in sys.argv:
        print(__encoding__)
    if "--license" in sys.argv or "-l" in sys.argv:
        print(__license__)
    if "--os" in sys.argv or "-os" in sys.argv:
        print(__os__)
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__help__)
