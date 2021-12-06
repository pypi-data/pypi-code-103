import platform
import shutil
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWizard, QSizePolicy, QSpacerItem

try:
    from ..__id__ import APP_NAME, ID
    from ..backend import logger
    from ..backend.constants import ConfigDirs, RootDirs
except (ValueError, ImportError):
    from __id__ import APP_NAME, ID
    from backend import logger
    from backend.constants import ConfigDirs, RootDirs

log = logger.new(__name__)


class HSpacer(QSpacerItem):
    def __init__(self, height: int, horizontalPolicy: QSizePolicy):
        policy = QSizePolicy.Minimum, horizontalPolicy
        super().__init__(0, height, *policy)


class Label(QtWidgets.QLabel):
    def __init__(self, pointSize: int = 8, text: str = "", bold: bool = False,
                 wrap: bool = False, center: bool = False):
        super().__init__()
        font = QtGui.QFont()
        font.setPointSize(pointSize)
        font.setBold(bold)
        self.setFont(font)
        self.setWordWrap(wrap)
        self.setText(text)
        if center:
            self.setAlignment(QtCore.Qt.AlignCenter)


class CheckableButton(QtWidgets.QPushButton):
    def __init__(self, path: Path):
        super().__init__()
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        icon = QtGui.QIcon(str(path))
        iconSize = icon.actualSize(QtCore.QSize(1024, 1024))
        self.setSizePolicy(sizePolicy)
        self.setIcon(icon)
        self.setIconSize(iconSize)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.setFlat(True)
        self.setText("")


class TrayButton(QtWidgets.QPushButton):
    def __init__(self):
        super().__init__("Manage taskbar")
        self.clicked.connect(self._clicked)

    def _clicked(self):
        """ Opens MS Windows Taskbar Settings """
        release = platform.release()
        cmd = "05D7B0F4-2121-4EFF-BF6B-ED3F69B894D9" if release == "7" else "0DF44EAA-FF21-4412-828E-260A8728E7F1"
        process = QtCore.QProcess()
        process.setArguments(["shell:::{" + cmd + "}"])
        process.setProgram("explorer")
        process.startDetached()


class Page(QtWidgets.QWizardPage):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setTitle(f"{APP_NAME} Customization Wizard")

    @property
    def sdb(self) -> dict:
        return self.core.sdb

    def done(self):
        pass


class PageHome(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setTitle("")
        self.setSubTitle("")
        titleLabel = Label(28, wrap=True, center=True, text=f"Welcome to {APP_NAME} !")
        greetLabel = Label(12, wrap=True)
        greetLabel.setText(f"This short wizard will guide you through the steps required to customize {APP_NAME} interface so it best fit your needs.")
        stepsLabel = Label(12, wrap=True)
        stepsLabel.setText("The following steps will let you choose some default settings :\n\n"
                           "‣ Note color palette\n"
                           "‣ Icon theme color\n"
                           "‣ Note frame style\n"
                           "‣ Text editing mode")

        layout = QtWidgets.QVBoxLayout()
        layout.addItem(HSpacer(20, QSizePolicy.Fixed))
        layout.addWidget(titleLabel)
        layout.addItem(HSpacer(30, QSizePolicy.Fixed))
        layout.addWidget(greetLabel)
        layout.addItem(HSpacer(30, QSizePolicy.Fixed))
        layout.addWidget(stepsLabel)
        layout.setContentsMargins(40, 30, 40, 30)
        self.setLayout(layout)


class PagePalette(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("Select a color palette")

        northernLabel = Label(center=True, text="\nNorthern")
        classicLabel = Label(center=True, text="\nClassic")
        graphiteLabel = Label(center=True, text="\nGraphite")

        self.graphiteButton = CheckableButton(RootDirs.WIZARD / "palette_graphite.png")
        self.northernButton = CheckableButton(RootDirs.WIZARD / "palette_northern.png")
        self.classicButton = CheckableButton(RootDirs.WIZARD / "palette_classic.png")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.graphiteButton, 0, 0, 1, 1)
        layout.addWidget(self.classicButton, 0, 1, 1, 1)
        layout.addWidget(self.northernButton, 0, 2, 1, 1)
        layout.addWidget(graphiteLabel, 1, 0, 1, 1)
        layout.addWidget(classicLabel, 1, 1, 1, 1)
        layout.addWidget(northernLabel, 1, 2, 1, 1)
        self.setLayout(layout)

    def done(self):
        """ Applies the checked value """
        if self.northernButton.isChecked():
            self.sdb["profile default"]["palette"] = "northern.css"
        elif self.classicButton.isChecked():
            self.sdb["profile default"]["palette"] = "classic.css"
        elif self.graphiteButton.isChecked():
            self.sdb["profile default"]["palette"] = "graphite.css"


class PageIconColor(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("Select the icon color that best match your theme")

        darkLabel = Label(center=True, text="\nDark menu icons for light themes")
        lightLabel = Label(center=True, text="\nLight menu icons for dark themes")

        self.darkButton = CheckableButton(RootDirs.WIZARD / "icons_dark.png")
        self.lightButton = CheckableButton(RootDirs.WIZARD / "icons_light.png")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.darkButton, 0, 0, 1, 1)
        layout.addWidget(self.lightButton, 0, 1, 1, 1)
        layout.addWidget(darkLabel, 1, 0, 1, 1)
        layout.addWidget(lightLabel, 1, 1, 1, 1)
        self.setLayout(layout)

    def done(self):
        if self.darkButton.isChecked():
            self.core.setMenuIconsColor("#404040")
        elif self.lightButton.isChecked():
            self.core.setMenuIconsColor("#8f8f8f")


class PageStyle(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("Select a frame style")

        minimalLabel = Label(bold=True, center=True, text="\nMinimal style")
        minimalDescLabel = Label(center=True, text="No toolbar, large resizing corners and more space for text")
        toolbarLabel = Label(bold=True, center=True, text="\nToolbar style")
        toolbarDescLabel = Label(center=True, text="Customizable toolbar with smaller resizing corners")

        self.minimalButton = CheckableButton(RootDirs.WIZARD / "style_minimal.png")
        self.toolbarButton = CheckableButton(RootDirs.WIZARD / "style_toolbar.png")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.minimalButton, 0, 0, 1, 1)
        layout.addWidget(self.toolbarButton, 0, 1, 1, 1)
        layout.addWidget(minimalLabel, 1, 0, 1, 1)
        layout.addWidget(toolbarLabel, 1, 1, 1, 1)
        layout.addWidget(minimalDescLabel, 2, 0, 1, 1)
        layout.addWidget(toolbarDescLabel, 2, 1, 1, 1)
        self.setLayout(layout)

    def done(self):
        if self.minimalButton.isChecked():
            self.sdb["profile default"]["style"] = "minimal.css"
        elif self.toolbarButton.isChecked():
            self.sdb["profile default"]["style"] = "toolbar.css"


class PageMode(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("Select a text editing mode")

        htmlLabel = Label(bold=True, center=True, text="\nRich text mode")
        htmlDescLabel = Label(center=True, text="Enable basic text decorations")
        plainLabel = Label(bold=True, center=True, text="\nPlain text mode")
        plainDescLabel = Label(center=True, text="Less featured, lighter and faster")
        vimLabel = Label(bold=True, center=True, text="\nVim mode")
        vimDescLabel = Label(text="Requires Linux, Vim and QTermWidget")

        self.htmlButton = CheckableButton(RootDirs.WIZARD / "mode_rich.png")
        self.plainButton = CheckableButton(RootDirs.WIZARD / "mode_plain.png")
        self.vimButton = CheckableButton(RootDirs.WIZARD / "mode_vim.png")
        self.vimButton.setEnabled("QTermWidget" in sys.modules)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.htmlButton, 0, 0, 1, 1)
        layout.addWidget(self.plainButton, 0, 1, 1, 1)
        layout.addWidget(self.vimButton, 0, 3, 1, 1)
        layout.addWidget(htmlLabel, 1, 0, 1, 1)
        layout.addWidget(plainLabel, 1, 1, 1, 1)
        layout.addWidget(vimLabel, 1, 3, 1, 1)
        layout.addWidget(htmlDescLabel, 2, 0, 1, 1)
        layout.addWidget(plainDescLabel, 2, 1, 1, 1)
        layout.addWidget(vimDescLabel, 2, 3, 1, 1)
        self.setLayout(layout)

    def done(self):
        if self.htmlButton.isChecked():
            self.sdb["profile default"]["mode"] = "html"
        elif self.plainButton.isChecked():
            self.sdb["profile default"]["mode"] = "plain"
        elif self.vimButton.isChecked():
            self.sdb["profile default"]["mode"] = "vim"


class PageLinux(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("You're all set !")

        doneLabel = Label(10, wrap=True, text="All done ! You may now right click on the tray icon to begin.")
        pixmap = QtGui.QPixmap(str(RootDirs.WIZARD / "tray_linux.png"))
        trayImgLabel = QtWidgets.QLabel()
        trayImgLabel.setPixmap(pixmap)
        trayImgLabel.setAlignment(QtCore.Qt.AlignCenter)
        trayTipLabel = Label(10)
        trayTipLabel.setText("<html><head/><body><p>No taskbar? Open the main menu from the command line :</p>"
                             f'<p><span style="font-weight:600;">{ID} -c menu</span></p>'
                             "</body></html>")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(doneLabel)
        layout.addItem(HSpacer(20, QSizePolicy.Fixed))
        layout.addWidget(trayImgLabel)
        layout.addItem(HSpacer(40, QSizePolicy.Fixed))
        layout.addWidget(trayTipLabel)
        layout.addItem(HSpacer(40, QSizePolicy.Expanding))
        self.setLayout(layout)


class PageWindows(Page):
    def __init__(self, core):
        super().__init__(core)
        self.setSubTitle("You're all set !")

        doneLabel = Label(10, wrap=True)
        doneLabel.setScaledContents(True)
        doneLabel.setText("<html><head/><body><p>All done ! You may now right click on the tray icon to begin.</p><hr/>"
                          "<p>It is recommended to set the taskbar icon as always shown. To do so, follow these simple steps :"
                          "</p></body></html>")

        step1Label = Label(wrap=True)
        step1Label.setText('<html><head/><body><p><span style="font-size:10pt;">1. Press the </span>'
                           '<span style="font-size:10pt; font-weight:600;">Manage taskbar</span>'
                           '<span style="font-size:10pt;"> button</span></p></body></html>')

        step2Label = Label(wrap=True)
        if platform.release() == "7":
            step2Path = "tray_w7_1.png"
            step3Path = "tray_w7_2.png"
            step2Label.setText('<html><head/><body><p><span style="font-size:10pt;">2. Uncheck </span>'
                               '<span style="font-size:10pt; font-weight:600;">Always show all icons and '
                               'notifications</span></p></body></html>')
        else:
            step2Path = "tray_w10_1.png"
            step3Path = "tray_w10_2.png"
            step2Label.setText('<html><head/><body><p><span style="font-size:10pt;">2. Under the </span>'
                               '<span style="font-size:10pt; font-weight:600;">Notification area</span>'
                               '<span style="font-size:10pt;"> category, click on </span>'
                               '<span style="font-size:10pt; font-weight:600;">Select which icons appear '
                               'on the taskbar</span></p></body></html>')

        step2Pixmap = QtGui.QPixmap(str(RootDirs.WIZARD / step2Path))
        step2ImgLabel = QtWidgets.QLabel()
        step2ImgLabel.setPixmap(step2Pixmap)

        step3Pixmap = QtGui.QPixmap(str(RootDirs.WIZARD / step3Path))
        step3Label = Label(wrap=True)
        step3Label.setText('<html><head/><body><p><span style="font-size:10pt;">3. Find and enable the </span>'
                           f'<span style="font-size:10pt; font-weight:600;">{APP_NAME}</span>'
                           '<span style="font-size:10pt;"> icon</span></p></body></html>')

        step3ImgLabel = QtWidgets.QLabel()
        step3ImgLabel.setPixmap(step3Pixmap)

        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        trayButton = TrayButton()
        trayButton.setFocusPolicy(QtCore.Qt.NoFocus)
        trayButton.setSizePolicy(sizePolicy)

        spacer = QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(doneLabel, 0, 0, 1, 5)
        layout.addItem(HSpacer(20, QSizePolicy.Expanding), 3, 0, 1, 1)
        layout.addWidget(step1Label, 2, 0, 1, 1)
        layout.addItem(HSpacer(40, QSizePolicy.Expanding), 1, 0, 1, 1)
        layout.addWidget(trayButton, 2, 2, 1, 1)
        layout.addItem(HSpacer(20, QSizePolicy.Expanding), 5, 0, 1, 1)
        layout.addWidget(step2Label, 4, 0, 1, 1)
        layout.addWidget(step2ImgLabel, 4, 2, 1, 1)
        layout.addItem(spacer, 2, 1, 1, 1)
        layout.addWidget(step3Label, 6, 0, 1, 1)
        layout.addWidget(step3ImgLabel, 6, 2, 1, 1)
        self.setLayout(layout)


class Wizard(QWizard):
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setWindowTitle(f"{APP_NAME} initial configuration wizard")
        self.resize(780, 460)
        self.setWizardStyle(QWizard.ModernStyle)
        self.accepted.connect(self._legacyPrompt)
        self.rejected.connect(self._legacyPrompt)

        pixmap = core.icons["settings"].pixmap(QtCore.QSize(32, 32))
        self.setPixmap(QWizard.LogoPixmap, pixmap)
        self.button(QWizard.NextButton).clicked.connect(self._next)

        self.addPage(PageHome(core))
        self.addPage(PagePalette(core))
        self.addPage(PageIconColor(core))
        self.addPage(PageStyle(core))
        self.addPage(PageMode(core))
        if sys.platform.startswith("win"):
            self.addPage(PageWindows(core))
        else:
            self.addPage(PageLinux(core))

    def _next(self):
        """ Calls done() method on the previous (now completed) page """
        last = self.currentId() - 1
        self.page(last).done()

    def _legacyPrompt(self):
        """ Proposes notes migration from a legacy version (former QtPad users) """
        qtpad = ConfigDirs.CFG.parent / "qtpad" / "notes"
        if qtpad.is_dir() and not self.core.sdb["legacy"]:
            prompt = ("Notes from an older version were found in the folder;\n"
                      f"'{qtpad}'\n\n"
                      f"Would you like to copy those into {APP_NAME} notes repository ?")
            dialog = QtWidgets.QMessageBox()
            answer = dialog.question(self, "QtPad Notes Migration", prompt, dialog.No | dialog.Yes, dialog.Yes)
            if answer == dialog.Yes:
                self._legacyCopy(qtpad)
        self.core.sdb["legacy"] = True

    def _legacyCopy(self, src: Path):
        """ Copy notes from a legacy version (former QtPad users) """
        files = [f for f in src.rglob("*.txt") if f.is_file()]
        files += [f for f in src.rglob("*.png") if f.is_file()]
        for f in files:
            dest = ConfigDirs.NOTES / f.relative_to(src)
            if dest.exists():
                log.info(f"Legacy : Ignored '{f}'")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, dest)
                log.info(f"Legacy : Copied '{f}'")
