from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFrame
from qfluentwidgets import (FluentWindow, SystemThemeListener, setTheme, Theme,
                            NavigationItemPosition)
from qfluentwidgets import FluentIcon as FIF

from .setting_interface_fluent import SettingInterface
from ..common.translator import Translator
from ..common import resources

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        self.themeListener = SystemThemeListener(self)
        setTheme(Theme.AUTO)

        self.settingInterface = SettingInterface(self)
        self.navigationInterface.setExpandWidth(215)
        self.navigationInterface.setAcrylicEnabled(True)

        self.initNavigation()

        self.themeListener.start()

    def initNavigation(self):
        t = Translator()
        # self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(463, 693)
        self.setMinimumWidth(300)
        self.setWindowIcon(QIcon(':/icons/icon.png'))
        self.setWindowTitle('HITSZ Connect Verge')
    
    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: setTheme(Theme.AUTO))
