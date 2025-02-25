from qfluentwidgets import (ScrollArea, ExpandLayout, SettingCardGroup, SwitchSettingCard,
                            PrimaryPushSettingCard)
from qfluentwidgets import FluentIcon as FIF

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from ..common.style_sheet import StyleSheet
from ..utils.check_for_update_fluent import check_for_updates


class SettingInterface(ScrollArea):
    """ Setting Interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("设置", self)
        self.updateSoftwareGroup = SettingCardGroup(
            title="软件更新", parent=self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            "启动时检查更新",
            configItem=None,
            parent=self.updateSoftwareGroup
        )
        self.updateOnStartUpCard.setFixedHeight(67)

        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            text="前往 GitHub",
            icon=FIF.FEEDBACK,
            title="提供反馈",
            content=None,
            parent=self.aboutGroup
        )
        self.feedbackCard.setFixedHeight(67)
        self.aboutCard = PrimaryPushSettingCard(
            text="检查更新",
            icon=FIF.INFO,
            title="关于",
            content='© ' + self.tr('Copyright') + " 2025, Kowyo. " +
            "当前版本"+ " " + "v1.0.0",
            parent=self.aboutGroup
        )

        self.__initWidget()
        self.__connectSignalToSlot()

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

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(15, 10, 15, 0)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        self.aboutCard.clicked.connect(
            lambda: check_for_updates(self, "1.0.0"))

        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/kowyo/hitsz-connect-verge/issues")))