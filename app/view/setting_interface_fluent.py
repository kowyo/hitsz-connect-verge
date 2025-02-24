from qfluentwidgets import (ScrollArea, ExpandLayout)

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt

from ..common.style_sheet import StyleSheet


class SettingInterface(ScrollArea):
    """ Setting Interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("设置", self)

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.__initLayout()

    def __initLayout(self):
        self.settingLabel.move(25, 20)