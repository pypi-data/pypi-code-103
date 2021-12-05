################################################################################
##
## BY: WANDERSON M.PIMENTA
## PROJECT MADE WITH: Qt Designer and PySide2
## V: 1.0.0
##
## This project can be used freely for all uses, as long as they maintain the
## respective credits only in the Python scripts, any information in the visual
## interface (GUI) can be modified without any implication.
##
## There are limitations on Qt licenses if you want to use your products
## commercially, I recommend reading them on the official website:
## https://doc.qt.io/qtforpython/licenses.html
##
################################################################################

class Style():

    style_bt_standard = (
    """
    QPushButton {
        background-image: ICON_REPLACE;
        background-position: left center;
        background-repeat: no-repeat;
        border: none;
        border-left: 28px solid rgb(27, 29, 35);
        background-color: rgb(27, 29, 35);
        text-align: left;
        padding-left: 45px;
    }
    QPushButton[Active=true] {
        background-image: ICON_REPLACE;
        background-position: left center;
        background-repeat: no-repeat;
        border: none;
        border-left: 28px solid rgb(27, 29, 35);
        border-right: 5px solid rgb(44, 49, 60);
        background-color: rgb(27, 29, 35);
        text-align: left;
        padding-left: 45px;
    }
    QPushButton:hover {
        background-color: rgb(63, 4, 70); /*rgb(33, 37, 43);*/
        border-left: 28px solid rgb(63, 4, 70);
    }
    QPushButton:pressed {
        background-color: rgb(85, 170, 255);
        border-left: 28px solid rgb(85, 170, 255);
    }
    """
    )

    style_custom = (
    """
    QPushButton {
        border: 2px solid rgb(52, 59, 72);
        border-radius: 5px; 
        background-color: rgb(52, 59, 72);
    }
    QPushButton:hover {
        background-color: rgb(57, 65, 80);
        border: 2px solid rgb(61, 70, 86);
    }
    QPushButton:pressed {   
        background-color: rgb(35, 40, 49);
        border: 2px solid rgb(43, 50, 61);
    }
    """
    )

    myGroupBoxStyle = '''
    QGroupBox {
        /*border: None;              /*<-----  None              */
        border: 1px solid #76797C;   /*<-----  1px solid #76797C */
        /* border-radius: 2px; */
        /* margin-top: 20px;*/
    }
    /* https://stackoverflow.com/questions/54408723/how-to-build-a-flat-groupbox-in-pyqt5
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding-left: 10px;
        padding-right: 10px;
        padding-top: 10px;
    }*/
    '''
    # app.setStyleSheet(myGroupBoxStyle)
