print('RUN main.py')
# import sys
# print('\tDebug sys.path:')
# for el in (sys.path):
#     print('\t', el)
from app_modules import *

class emyMainWindow(QMainWindow):
    def __init__(self, ui=None):
        QMainWindow.__init__(self) # QMainWindow.__init__(self, None, Qt.WindowStayclssOnTopHint | Qt.FramelessWindowHint) # always on top

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ## PRINT ==> SYSTEM
            # 📕: error message
            # 📙: warning message
            # 📗: ok status message
            # 📘: action message
            # 📓: canceled status message
            # 📔: Or anything you like and want to recognize immediately by color
        print('\t📗 [yellow]System[/]: ' + platform.system())
        print('\t📗 [yellow]Version[/]: '+ platform.release())

        ########################################################################
        ## START - WINDOW ATTRIBUTES
        ########################################################################

        ## REMOVE ==> STANDARD TITLE BAR
        UIFunctions.removeTitleBar(True)


        ## SET ==> WINDOW TITLE
        # self.setWindowTitle('Main Window - emachinery')
        UIFunctions.labelTitle(self, 'Main Window - emachinery - Idling')
        UIFunctions.labelDescription(self, 'GUI for electric machinery analysis')


        ## WINDOW SIZE ==> DEFAULT SIZE
        startSize = QSize(1440, 1080)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # UIFunctions.enableMaximumSize(self, 500, 720)


        ## ==> CREATE MENUS
        ########################################################################

        ## ==> TOGGLE MENU SIZE
        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))


        ## ==> ADD CUSTOM MENUS
        self.ui.stackedWidget.setMinimumWidth(20)

        # files.qrc (url is defined in this qrc file), alternatively, you can specify the absolute locaiton.
        # UIFunctions.addNewMenu(self, "Name Plate Data",     "btn_namePlateData",     f"url({parent_dir}icons/16x16/cil-input.png)", True)
        UIFunctions.addNewMenu(self, "Name Plate Data",     "btn_namePlateData",     "url(:/16x16/icons/16x16/cil-input.png)", True)
        UIFunctions.addNewMenu(self, "Controller Tuning",   "btn_controllerTuning",  "url(:/16x16/icons/16x16/cil-loop.png)", True)
        UIFunctions.addNewMenu(self, "C-based Simulation",  "btn_cBasedSimulation",  "url(:/16x16/icons/16x16/cil-reload.png)", True)
        UIFunctions.addNewMenu(self, "Scope",               "btn_scope",             "url(:/16x16/icons/16x16/cil-chart-line.png)", True)
        UIFunctions.addNewMenu(self, "Plots",               "btn_plots",             "url(:/16x16/icons/16x16/cil-history.png)", True)
        UIFunctions.addNewMenu(self, "Parametric Analysis", "btn_parametricAnalysis","url(:/16x16/icons/16x16/cil-layers.png)", True)
        UIFunctions.addNewMenu(self, "Add User",            "btn_new_user",          "url(:/16x16/icons/16x16/cil-user-follow.png)", True)
        UIFunctions.addNewMenu(self, "HOME",                "btn_home",              "url(:/16x16/icons/16x16/cil-home.png)", True)
        UIFunctions.addNewMenu(self, "Py-based Simulation", "btn_pyBasedSimulation", "url(:/16x16/icons/16x16/cil-chevron-double-down.png)", False)
        UIFunctions.addNewMenu(self, "Custom Widgets",      "btn_widgets",           "url(:/16x16/icons/16x16/cil-equalizer.png)", False) # False goes to bottom

        # START MENU => SELECTION
        # UIFunctions.selectStandardMenu(self, "btn_home")
        UIFunctions.selectStandardMenu(self, "btn_cBasedSimulation")
        # if True:
        #     self.ui.stackedWidget.setCurrentWidget(self.ui.page_cBasedSimulation)
        #     UIFunctions.resetStyle(self, "btn_cBasedSimulation")
        #     UIFunctions.labelPage(self, "C-based Simulation")
        #     # btnWidget = self.ui.btn_cBasedSimulation
        #     # btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))


        ## ==> START PAGE
        # self.ui.stackedWidget.setCurrentWidget(self.ui.page_home)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_cBasedSimulation)


        ## USER ICON ==> SHOW HIDE
        UIFunctions.userIcon(self, "CJH", "url(:/16x16/icons/16x16/cil-user.png)", True)
        # UIFunctions.userIcon(self, "CJH", "", True)



        ## ==> MOVE WINDOW / MAXIMIZE / RESTORE
        ########################################################################
        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if UIFunctions.returStatus() == 1:
                UIFunctions.maximize_restore(self)

            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        # WIDGET TO MOVE
        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow


        ## ==> LOAD DEFINITIONS
        ########################################################################
        UIFunctions.uiDefinitions(self)


        ########################################################################
        ## END - WINDOW ATTRIBUTES
        ############################## ---/--/--- ##############################




        ########################################################################
        #                                                                      #
        ## START -------------- WIDGETS FUNCTIONS/PARAMETERS ---------------- ##
        #                                                                      #
        ## ==> USER CODES BELLOW                                              ##
        ########################################################################



        ## ==> QTableWidget RARAMETERS
        ########################################################################
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


        ## ==> AppFunctions Initialization
        AppFunctions.initialize_connections(self)
        # self.ui.ConsoleWidget.show() # TODO this used to give me a separate window console, but it


        # self.ui.ConsoleWidget.setStyleSheet(self.ui.ConsoleWidget.styleSheet() + "background: rgb(27, 29, 35);")
        # self.ui.plainTextEdit_ACMPlotLabels.setStyleSheet(self.ui.plainTextEdit_ACMPlotLabels.styleSheet() + "background: rgb(27, 29, 35);")
        # print('DEBUG:', self.ui.ConsoleWidget.styleSheet())
        # print('|||')
        # print('DEBUG:', self.ui.plainTextEdit_ACMPlotLabels.styleSheet())
        # self.ui.ConsoleWidget.setStyleSheet("background: rgb(27, 29, 35);")
        # self.ui.ConsoleWidget.setStyleSheet("background: transparent;")

        ########################################################################
        #                                                                      #
        ## END --------------- WIDGETS FUNCTIONS/PARAMETERS ----------------- ##
        #                                                                      #
        ############################## ---/--/--- ##############################


        ## SHOW ==> MAIN WINDOW
        ########################################################################
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint) # always on top
        # self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive) # https://stackoverflow.com/questions/42614623/how-to-make-a-pyside-window-pop-up-above-all-other-windows
        self.activateWindow()

        # self.setWindowState(QtCore.Qt.WindowMaximized)
        # self.show()
            # self.showFullScreen()
            # self.showMaximized()
            # self.ui.show()



        ########################################################################
        #                                                                      #
        ## START -------------- Add CSS for Pormoted Widgets ---------------- ##
        #                                                                      #
        ## ==> USER CODES BELLOW                                              ##
        ########################################################################

        # 颜色设置
        # 为什么初始化的时候设置css无效？而是必须在这里事后设置呢？？
        # 为什么无法修改ConsoleWidget和QCodeEditor的背景色呢？
        css = '''
        color: blue;
        background-color: yellow;
        selection-color: yellow;
        selection-background-color: blue;
        '''
        css = '''
        color: #ff6347;
        background-color: #272822;
        selection-color: #272822;
        selection-background-color: #d5d1c7;
        '''
        # print('{debug app_functions.py}: apply css loc 2')
        self.ui.ConsoleWidget.setStyleSheet(css)
        self.ui.plainTextEdit_ACMPlotLabels.setStyleSheet(css)
        self.ui.plainTextEdit_ACMPlotDetails.setStyleSheet(css)
        self.ui.plainTextEdit_LissajousPlotSignals.setStyleSheet(css)
        self.ui.plainTextEdit_PANames.setStyleSheet(css)
        self.ui.plainTextEdit_PAValues.setStyleSheet(css)

        self.ui.pushButton_ACMPlotHere
        self.ui.pushButton_ACMPlotHereAtTop
        self.ui.pushButton_runCBasedSimulation
        self.ui.pushButton_updateModel  
        self.ui.pushButton_pidTuner
        self.ui.pushButton_LissajousPlot
        self.ui.pushButton_getSignal
        self.ui.pushButton_runCBasedSimulation4PA
        self.ui.pushButton_plot4PA
        self.ui.pushButton_bodePlot

        ########################################################################
        #                                                                      #
        ## END --------------- Add CSS for Pormoted Widgets ----------------- ##
        #                                                                      #
        ############################## ---/--/--- ##############################

    ########################################################################
    ## MENUS ==> DYNAMIC MENUS FUNCTIONS
    ########################################################################
    def Button(self):
        # GET BT CLICKED
        btnWidget = self.sender()
        # print('DEBUG: ', btnWidget)

        dict_object = OD({
                'btn_home': 
                    {
                        'page': self.ui.page_home,
                        'label': "Home"
                    },
                'btn_new_user':
                    {
                        'page': self.ui.page_home,
                        'label': "New User"
                    },
                'btn_namePlateData':
                    {
                        'page': self.ui.page_namePlateData,
                        'label': "Name Plate Data",
                    },
                'btn_controllerTuning':
                    {
                        'page': self.ui.page_controllerTuning,
                        'label': "Controller Tuning",
                    },
                'btn_cBasedSimulation':
                    {
                        'page': self.ui.page_cBasedSimulation,
                        'label': "C-based Simulation",
                    },
                'btn_pyBasedSimulation':
                    {
                        'page': self.ui.page_PyBasedSimulation,
                        'label': "Py-based Simulation",
                    },
                'btn_plots':
                    {
                        'page': self.ui.page_plots,
                        'label': "Plots",
                    },
                'btn_scope':
                    {
                        'page': self.ui.page_scope,
                        'label': "Scope",
                    },
                'btn_parametricAnalysis':
                    {
                        'page': self.ui.page_parametricAnalysis,
                        'label': "Parametric Analysis",
                    },
                'btn_widgets':
                    {
                        'page': self.ui.page_widgets,
                        'label': "Custom Widgets"
                    }
            })

        for key, d in dict_object.items():

            if btnWidget.objectName() == key:
                self.ui.stackedWidget.setCurrentWidget(d['page'])
                UIFunctions.resetStyle(self, key)
                UIFunctions.labelPage(self, d['label'])
                btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet(), this=self))

    ########################################################################
    ## START ==> APP EVENTS
    ########################################################################

    ## EVENT ==> MOUSE DOUBLE CLICK
    ########################################################################
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())

    ## EVENT ==> MOUSE CLICK
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
        if event.buttons() == Qt.MidButton:
            print('Mouse click: MIDDLE BUTTON')

    ## EVENT ==> KEY PRESSED
    ########################################################################
    def keyPressEvent(self, event):
        print('[emyMainWindow] Key: ' + str(event.key()) + ' | Text Press: ' + str(event.text()))

        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_F11:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        elif event.key() == QtCore.Qt.Key_C:
            UIFunctions.selectStandardMenu(self, "btn_cBasedSimulation")
            UIFunctions.labelTitle(self, 'Main Window - emachinery - Jump to page_cBasedSimulation')
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_cBasedSimulation)
        elif event.key() == QtCore.Qt.Key_S:
            UIFunctions.selectStandardMenu(self, "btn_scope")
            UIFunctions.labelTitle(self, 'Main Window - emachinery - Jump to page_scope')
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_scope)
        elif event.key() == QtCore.Qt.Key_B:
            if self.ui.stackedWidget.currentIndex() == 4: # 4 -> page_cBasedSimulation
                UIFunctions.labelTitle(self, 'Main Window - emachinery - Build')
                AppFunctions.runCBasedSimulation(self)
        # elif event.key() == QtCore.Qt.Key_Z:
        #     AppFunctions.user_shortcut(self, event)
        else:
            super(emyMainWindow, self).keyPressEvent(event) # Do the default action on the parent class QLineEdit

    ## EVENT ==> Focus In
    ########################################################################
    def focusInEvent(self, event):
        # Do something with the event here
        super(emyMainWindow, self).focusInEvent(event) # Do the default action on the parent class QLineEdit

    ## EVENT ==> RESIZE EVENT
    ########################################################################
    def resizeEvent(self, event):
        self.resizeFunction()
        return super(emyMainWindow, self).resizeEvent(event)

    def resizeFunction(self):
        print('\t📗 [yellow]Height:[/]' + str(self.height()) + ' | [yellow]Width:[/] ' + str(self.width()))

    ########################################################################
    ## END ==> APP EVENTS
    ############################## ---/--/--- ##############################


# Watch Expressions
# ///////////////////////////////////////////////////////////////
# from PySide2.QtWidgets import QLineEdit
class expressionWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Figure: Watch Expressions')
        mainLayout = QVBoxLayout()
        self.input1 = QLineEdit()
        mainLayout.addWidget(self.input1)
        self.setLayout(mainLayout)


if bool_load_PyBlackBox: # 类的定义不能放到 app_modules.py！
    # IPython as Console
    # ///////////////////////////////////////////////////////////////
    class PyBlackBox_MainWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            # GET WIDGETS FROM "ui_main.py"
            # Load widgets inside MainWindow
            # ///////////////////////////////////////////////////////////////
            self.ui = Ui_PyBlackBox()
            self.ui.setupUi(self)

            # SET DEFAULT PAGE
            # ///////////////////////////////////////////////////////////////
            # self.ui.app_pages.setCurrentWidget(self.ui.home)
            self.ui.app_pages.setCurrentWidget(self.ui.page_console)

            # LOAD DICT SETTINGS FROM "settings.json" FILE
            # ///////////////////////////////////////////////////////////////
            self.settings = Settings()

            self.custom_btn_top = LeftMenuButton(
                self,
                "custom_btn_top",
                "images/icons_svg/icon_add_user.svg",
                "Add new friend"
            )
            self.custom_btn_top_2 = LeftMenuButton( # THE SCOPE
                parent=self,
                name="custom_btn_top_2_Scope",
                icon="images/icons_png/cil-chart-line.png",
                tooltip="View real-time waveforms"
            )
            self.custom_btn_top_3 = LeftMenuButton( # THE CONSOLE
                parent=self,
                name="custom_btn_top_3_Console",
                icon="images/icons_svg/icon_send.svg",
                tooltip="IPython console"
            )
            self.custom_btn_bottom_1 = LeftMenuButton(
                self,
                "custom_btn_bottom_1",
                "images/icons_svg/icon_more_options.svg",
                "More options, test with many words"
            )
            self.custom_btn_bottom_2 = LeftMenuButton(
                self,
                "custom_btn_bottom_2",
                "images/icons_svg/icon_settings.svg",
                "Open settings"
            )
            self.ui.top_menus_layout.addWidget(self.custom_btn_top)
            self.ui.top_menus_layout.addWidget(self.custom_btn_top_2)
            self.ui.top_menus_layout.addWidget(self.custom_btn_top_3)
            self.ui.bottom_menus_layout.addWidget(self.custom_btn_bottom_1)
            self.ui.bottom_menus_layout.addWidget(self.custom_btn_bottom_2)

            # DEBUG
            self.custom_btn_top.clicked.connect(      lambda: print(f"{self.settings['app_name']}: clicked"))
            self.custom_btn_top.released.connect(     lambda: print(f"{self.custom_btn_top.objectName()}: released"))
            self.custom_btn_top_2.clicked.connect(    lambda: self.ui.app_pages.setCurrentWidget(self.ui.page_scope))
            self.custom_btn_top_3.clicked.connect(    lambda: self.ui.app_pages.setCurrentWidget(self.ui.page_console))
            self.custom_btn_bottom_1.clicked.connect( lambda: print(f"{self.custom_btn_bottom_1.objectName()}: clicked"))
            self.custom_btn_bottom_1.released.connect(lambda: print(f"{self.custom_btn_bottom_1.objectName()}: released"))
            self.custom_btn_bottom_2.clicked.connect( lambda: print(f"{self.custom_btn_bottom_2.objectName()}: clicked"))
            self.custom_btn_bottom_2.released.connect(lambda: print(f"{self.custom_btn_bottom_2.objectName()}: released"))

            # TOP USER BOX
            # Add widget to App
            # ///////////////////////////////////////////////////////////////
            self.top_user = TopUserInfo(self.ui.left_messages, 8, 64, "Hory", "Writing python codes")
            self.top_user.setParent(self.ui.top_user_frame)
            self.top_user.status.connect(self.status_change)

            # SET UI DEFINITIONS
            # Run set_ui_definitions() in the ui_functions.py
            # ///////////////////////////////////////////////////////////////
            ui_functions.UiFunctions.set_ui_definitions(self)

            # ADD MESSAGE BTNS / FRIEND MENUS
            # Add btns to page
            # ///////////////////////////////////////////////////////////////
            parent_dir = os.path.dirname(__file__)
            add_user = [ # CJH: the parent directory is emachinery, so I need to add guiv2/ here for user_image
                {
                    "user_image" : f"{parent_dir}/images/users/cat.png",
                    "user_name" : "Tom",
                    "user_description" : "Did you see a mouse?",
                    "user_status" : "online",
                    "unread_messages" : 2,
                    "is_active" : False
                },
                {
                    "user_image" : f"{parent_dir}/images/users/mouse.png",
                    "user_name" : "Jerry",
                    "user_description" : "I think I saw a cat...",
                    "user_status" : "busy",
                    "unread_messages" : 1,
                    "is_active" : False
                },
                {
                    "user_image" : f"{parent_dir}/images/users/me.png",
                    "user_name" : "Me From The Future",
                    "user_description" : "Lottery result...",
                    "user_status" : "invisible",
                    "unread_messages" : 0,
                    "is_active" : False
                }
            ]
            self.menu = FriendMessageButton
            def add_menus(self, parameters):
                id = 0
                for parameter in parameters:

                    user_image = parameter['user_image']
                    user_name = parameter['user_name']
                    user_description = parameter['user_description']
                    user_status = parameter['user_status']
                    unread_messages = parameter['unread_messages']
                    is_active = parameter['is_active']

                    self.menu = FriendMessageButton(
                        id, user_image, user_name, user_description, user_status, unread_messages, is_active
                    )
                    self.menu.clicked.connect(self.btn_clicked)
                    self.menu.released.connect(self.btn_released)
                    self.ui.messages_layout.addWidget(self.menu)
                    id += 1

            add_menus(self, add_user)


            # 颜色设置
            # 为什么初始化的时候设置css无效？而是必须在这里事后设置呢？？
            # 为什么无法修改ConsoleWidget和QCodeEditor的背景色呢？
            css = '''
            color: blue;
            background-color: yellow;
            selection-color: yellow;
            selection-background-color: blue;
            '''
            css = '''
            color: #ff6347;
            background-color: #272822;
            selection-color: #272822;
            selection-background-color: #d5d1c7;
            '''
            # print('{debug app_functions.py}: apply css loc 2')
            self.ui.PBB_ConsoleWidget.setStyleSheet(css)
            # self.ui.PBB_ConsoleWidget.setStyleSheet(None)
            # print('DEBUG:', self.ui.PBB_ConsoleWidget)
            # print('DEBUG:', self.ui.PBB_ConsoleWidget.setStyleSheet(None))

            # SHOW MAIN WINDOW
            # ///////////////////////////////////////////////////////////////
            self.show()

        # SET USERNAME TO MAIN WINDOW
        # ///////////////////////////////////////////////////////////////
        def set_user_and_description(self, username):
            self.top_user.user_name = username
            print(f"User: {username} are logged!")

        # PRINT STATUS
        # ///////////////////////////////////////////////////////////////
        def status_change(self, status):
            print(f"send signal: {status}")

        # GET BTN CLICKED
        # ///////////////////////////////////////////////////////////////
        def btn_clicked(self):
            # GET BT CLICKED
            btn = self.sender()

            # UNSELECT CHATS
            ui_functions.UiFunctions.deselect_chat_message(self, btn.objectName())

            # SELECT CLICKED
            if btn.objectName():
                btn.reset_unread_message()
                ui_functions.UiFunctions.select_chat_message(self, btn.objectName())

            # LOAD CHAT PAGE
            if btn.objectName():
                # REMOVE CHAT
                for chat in reversed(range(self.ui.chat_layout.count())):
                    self.ui.chat_layout.itemAt(chat).widget().deleteLater()
                self.chat = None

                # SET CHAT WIDGET
                self.chat = Chat(btn.user_image, btn.user_name, btn.user_description, btn.objectName(), self.top_user.user_name)

                # ADD WIDGET TO LAYOUT
                self.ui.chat_layout.addWidget(self.chat)

                # JUMP TO CHAT PAGE
                self.ui.app_pages.setCurrentWidget(self.ui.chat)

            # DEBUG
            print(f"Button {btn.objectName()}, clicked!")

        # GET BTN RELEASED
        # ///////////////////////////////////////////////////////////////
        def btn_released(self):
            # GET BT CLICKED
            btn = self.sender()
            print(F"Button {btn.objectName()}, released!")


        # RESIZE EVENT
        # Whenever the window is resized, this event will be triggered
        # ///////////////////////////////////////////////////////////////
        def resizeEvent(self, event):
            ui_functions.UiFunctions.resize_grips(self)

        # MOUSE CLICK EVENTS
        # ///////////////////////////////////////////////////////////////
        def mousePressEvent(self, event):
            # SET DRAG POS WINDOW
            self.dragPos = event.globalPos()


def startApp():

    app = QApplication(sys.argv)
    # window = LoginWindow()
    # window.show()

    # SHOW MAIN WINDOWB
    main = emyMainWindow()
    main.show()

    # SHOW Watch Expressions
    main.eW = None
    # main.eW = expressionWindow()
    # main.eW.show()

    if bool_load_PyBlackBox:
        # SHOW PBB as IPython Console
        main.pbb = PyBlackBox_MainWindow()
        main.pbb.top_user.label_user.setText('hory'.capitalize()) # 更新用户名
        main.pbb.show()

    if bool_use_PySide6:
        sys.exit(app.exec())
    elif bool_use_PyQt5:
        app.exec_()
    else:
        sys.exit(app.exec_())

if __name__ == "__main__":

    # TestStyle = '''
    # ConsoleWidget{
    #     background-color: rgb(100, 100, 100);
    # }
    # '''
    # app.setStyleSheet(TestStyle)

    # QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    # QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')

    # print('Login window 2 elapsed:', time.time() - global_time)
    # window = LoginWindow()
    # window.show()

    print('\tElapsed: import modules:', time.time() - global_time)
    BOOL_MAIN_WINDOW_OPENED = True
    startApp() # QTimer.singleShot(1, startApp)
