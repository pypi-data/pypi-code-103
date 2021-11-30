#import sys
#
import threading
from datetime import date

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

#from fime.config import Config
#from import_task import ImportTask
#
#app = QtWidgets.QApplication()
#QtCore.QCoreApplication.setApplicationName("fime")
#nt = ImportTask(Config(), None)
#nt.show()
#
#app.exec_()
#print(r.report())
#print(r._actual_data_len)
#print(r.report()[:r._actual_data_len])
#print(l._data["2020-02"].keys())
#import datetime
#
#from PySide2 import QtCore
#
#from config import Config
#from worklog_ import Worklog
#
#QtCore.QCoreApplication.setApplicationName("fime")
#
#w = Worklog(Config())
#w.get("ASG-8690", datetime.date(2021, 10, 26))
#w.get("ASG-9999", datetime.date(2021, 10, 29))

import time
import random
from fime.config import Config
from fime.worklog import WorklogDialog
from fime.data import Data, LogCommentsData, Worklog
from fime.data import dEV

dEV = True

app = QtWidgets.QApplication()
QtCore.QCoreApplication.setApplicationName("fime")
wl = WorklogDialog(Config(), None)

data = Data()
lcd = LogCommentsData(data)
wld = Worklog(lcd)
#wld._date = date(2021,11,27)
wl.set_data(wld)
wl.show()

app.exec_()
