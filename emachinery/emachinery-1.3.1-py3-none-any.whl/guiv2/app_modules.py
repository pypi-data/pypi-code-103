print('RUN app_modules')
# Python Packages
import sys, platform, os, builtins, time
from win32api import GetComputerName
from rich import print

# GLOBALS
# ///////////////////////////////////////////////////////////////
counter = 0
builtins.parent_dir = os.path.dirname(__file__) + '/'
BOOL_MAIN_WINDOW_OPENED = False

global_time = time.time()

bool_load_PyBlackBox = True
bool_use_PyQt5 = False
bool_use_PySide6 = False # bool_use_PySide6 = True if sys.version_info[1] > 8 else False
''' Cannot use PySide6 as mpl does not support it yet '''
''' 切换到python3.9+PySide6，需要做三件事：
第一件事，VSCode下面Python Interpreter切换为python 3.9；
第二件事，令bool_use_PySide6=True；
第三件事，运行.venv 下面的 Scripts/activate，然后运行guiv2/ui2py_pyside6.bat更新.ui文件对应的.py文件。
'''
builtins.pcname = GetComputerName()
print('\tPC name:', builtins.pcname)
print(f'\tpython version: {sys.version_info[0]}.{sys.version_info[1]}')

# QT Packages
if bool_use_PySide6:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, Signal, QEasingCurve, QTimer)
    from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QPen, QPainterPath, QImage)
    from PySide6.QtWidgets import * # QApplication, QMainWindow, QPushButton, QSizePolicy, QWidget, QLineEdit

elif not bool_use_PyQt5:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, Signal, QEasingCurve, QTimer)
    from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QPen, QPainterPath, QImage)
    from PySide2.QtWidgets import * # QApplication, QMainWindow, QPushButton, QSizePolicy, QWidget, QLineEdit

    # PySide2 doBBes not allow what you have been doing with PyQt5. So, just don't use LoadUi().
    # Debug from .ui file;                     # This Suppress a web-engine warning
    # from PySide2.QtUiTools import QUiLoader; QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
else:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent, Signal, QEasingCurve, QTimer)
    from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient, QPen, QPainterPath, QImage)
    from PyQt5.QtWidgets import * # QApplication, QMainWindow, QPushButton, QSizePolicy


# GUI FILE
# Load .py file conveted from GUI_BASE.ui
from ui_main import Ui_MainWindow

# IMPORT QSS CUSTOM
from ui_styles import Style

# IMPORT FUNCTIONS
from ui_functions_old import *

## ==> APP FUNCTIONS
from app_functions import *


if bool_load_PyBlackBox:
    # LOGIN
    from circular_progress import CircularProgress
    from ui_login import Ui_Login # Login / Splash Screen
    # ///////////////////////////////////////////////////////////////
    class LoginWindow(QMainWindow):

        def __init__(self):
            QMainWindow.__init__(self)
            # GET WIDGETS FROM "ui_login.py"
            # Load widgets inside LoginWindow
            # ///////////////////////////////////////////////////////////////
            self.ui = Ui_Login()
            self.ui.setupUi(self)

            # REMOVE TITLE BAR
            # ///////////////////////////////////////////////////////////////
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setAttribute(Qt.WA_TranslucentBackground)

            # IMPORT CIRCULAR PROGRESS
            # ///////////////////////////////////////////////////////////////
            self.progress = CircularProgress()
            self.progress.width = 240
            self.progress.height = 240
            self.progress.value = 0
            self.progress.setFixedSize(self.progress.width, self.progress.height)
            self.progress.font_size = 20
            self.progress.add_shadow(True)
            self.progress.progress_width = 4
            self.progress.progress_color = QColor("#bdff00")
            self.progress.text_color = QColor("#E6E6E6")
            self.progress.bg_color = QColor("#222222")
            self.progress.setParent(self.ui.preloader)
            self.progress.show()

            # ADD DROP SHADOW
            # ///////////////////////////////////////////////////////////////
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(15)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.ui.bg.setGraphicsEffect(self.shadow)

            # QTIMER
            # ///////////////////////////////////////////////////////////////
            self.timer = QTimer()
            self.timer.timeout.connect(self.update)
            self.timer.start(15) # 30 # change the time needed for progress bar to finish

            # KEY PRESS EVENT
            # ///////////////////////////////////////////////////////////////
            self.ui.username.keyReleaseEvent = self.check_login
            self.ui.password.keyReleaseEvent = self.check_login
            self.check_login(None)

        # CHECK LOGIN
        # ///////////////////////////////////////////////////////////////
        def check_login(self, event):

            # if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            username = 'Hory'   # self.ui.username.text()
            password = '123456' # self.ui.password.text()
            # username = self.ui.username.text()
            # password = self.ui.password.text()

            def open_main():

                # PyBlackBox_MainWindow().show()

                # # SHOW MAIN WINDOW
                # self.main = emyMainWindow()
                # self.main.show()

                # # SHOW Watch Expressions
                # self.main.eW = expressionWindow()
                # self.main.eW.show()

                # # SHOW PBB as IPython Console
                # self.main.pbb = PyBlackBox_MainWindow()
                # self.main.pbb.top_user.label_user.setText(username.capitalize()) # 更新用户名
                # self.main.pbb.show()

                self.close()

            if username and password == "123456":
                self.ui.user_description.setText(f"Welcome {username}!")
                self.ui.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid #bdff00; }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                QTimer.singleShot(2*1200, lambda: open_main())
            else:
                # SET STYLESHEET
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid rgb(255, 0, 127); }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                self.shacke_window()


        def shacke_window(self):
            # SHACKE WINDOW
            actual_pos = self.pos()
            QTimer.singleShot(0, lambda: self.move(actual_pos.x() + 1, actual_pos.y()))
            QTimer.singleShot(50, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
            QTimer.singleShot(100, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
            QTimer.singleShot(150, lambda: self.move(actual_pos.x() + -5, actual_pos.y()))
            QTimer.singleShot(200, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
            QTimer.singleShot(250, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
            QTimer.singleShot(300, lambda: self.move(actual_pos.x(), actual_pos.y()))

        # UPDATE PROGRESS BAR
        # ///////////////////////////////////////////////////////////////
        def update(self):
            global counter

            # SET VALUE TO PROGRESS BAR
            self.progress.set_value(counter)

            # CLOSE SPLASH SCREEN AND OPEN MAIN APP
            if counter >= 100:
                # STOP TIMER
                self.timer.stop()
                self.animation_login()

                # CJH: kill itself when finish circular progress
                # self.close()

            # INCREASE COUNTER
            counter += 1

        # START ANIMATION TO LOGIN
        # ///////////////////////////////////////////////////////////////
        def animation_login(self):
            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.frame_widgets, b"geometry")
            self.animation.setDuration(1500)
            self.animation.setStartValue(QRect(0, 70, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
            self.animation.setEndValue(QRect(0, -325, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

            # CJH: kill itself after login shows up
            # self.close()

    # PyBlackBox GUI FILE
    from ui_main_pyblackbox import Ui_MainWindow as Ui_PyBlackBox
    from ui_page_messages import Ui_chat_page

    # PyBlackBox utilities
    from settings import Settings # will be used in the following package (the import order matters)
    from left_menu_button import LeftMenuButton
    from top_user_box import TopUserInfo
    from custom_grips import CustomGrip # before import ui_functions_pbb
    from friend_message_button import FriendMessageButton
    from message import Message
    from page_messages import Chat
    import ui_functions_pbb as ui_functions

    Help = r''' 
        If you want to import a new module (say tuner) in a new directory (e.g., acmdesignv2), you need to follow these steps:

        1. Open __init__.py in emachinery folder, and add path to new directory to sys.
        2. Create an __init__.py file inside your new directory.
        3. Delete emachinery.egg-info/ and other temporary folders (build, dist) if there are.
        3. Cd to D:\DrH\Codes\emachineryTestPYPI and do: pip install -e .
        4. You will see following message:
            ---------------------------
            D:\DrH\Codes\emachineryTestPYPI>pip install -e .
            Obtaining file:///D:/DrH/Codes/emachineryTestPYPI
            Installing collected packages: emachinery
            Attempting uninstall: emachinery
                Found existing installation: emachinery 1.0.3
                Uninstalling emachinery-1.0.3:
                Successfully uninstalled emachinery-1.0.3
            Running setup.py develop for emachinery
            Successfully installed emachinery

        Or else,
        You are going to see the following error message when running:
            ---------------------------
            Traceback (most recent call last):
            File "D:\DrH\Codes\emachineryTestPYPI\emachinery\gui\main.py", line 28, in <module>
                from emachinery.acmdesignv2 import tuner
            ModuleNotFoundError: No module named 'emachinery.acmdesignv2'

        5. After you pip install from PyPI, if you see error message similar to:
            'EmachineryWidget' object has no attribute 'lineEdit_path2boptPython'
        this is likely that you should call self.ui.lineEdit_path2boptPython instead of self.lineEdit_path2boptPython.
        This is not a problem if you load .ui, but it is a problem if you import .py obtained via pyuic5.

        6. 还有一个不方便的地方就是，如果正式安装了emachinery，就没法在本地测试了，因为会优先import库emachinery中的.py文件作为模块。
        换句话说，只能用“pip install -e .”进行本地测试。
    '''
    KnownIssues=r'''
        - If a function is connected, the first *arg is always set to True or False by PyQt5. Search for bool_always_[\D]*_bug for example.
            - This does not occur if I use a lambda when calling connect
            - A solution is provided in https://stackoverflow.com/questions/60001583/pyqt5-slot-function-does-not-take-default-argument
        - QPainter not active bug
            - It is because of the svg files are not included in Manifest.in file.
            - see https://stackoverflow.com/questions/16192142/qtpainter-error-paint-device-returned-engine-0-type-3-painter-not-active
            - see more, https://zetcode.com/gui/pyqt4/drawing/
    '''

