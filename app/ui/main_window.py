from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.ui.adventure_view import AdventureView
from app.ui.hero_workshop_view import HeroWorkshopView
from app.ui.home_view import HomeView
from app.ui.settings_dialog import SettingsDialog


APP_STYLE = """
QWidget {
    background: #12100d;
    color: #f4eadb;
    font-size: 14px;
}
QLabel#HeroTitle {
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 2px;
}
QLabel#Subtitle, QLabel#Muted {
    color: #b8aa96;
}
QLabel#CardTitle {
    font-size: 18px;
    font-weight: 600;
}
QFrame#Panel, QFrame#CampaignCard, QFrame#ChoiceCard {
    background: #1c1813;
    border: 1px solid #3b2f22;
    border-radius: 14px;
}
QFrame#ChoiceCard:hover {
    background: #251f17;
    border-color: #8a5a24;
}
QRadioButton {
    spacing: 8px;
    padding: 4px;
}
QTextEdit, QLineEdit, QComboBox {
    background: #211c16;
    border: 1px solid #4a3a28;
    border-radius: 10px;
    padding: 8px;
    selection-background-color: #8f6a3a;
}
QTextEdit#Narration {
    font-size: 15px;
    line-height: 1.4;
}
QPushButton {
    background: #2b241b;
    border: 1px solid #5a4630;
    border-radius: 10px;
    padding: 9px 14px;
}
QPushButton:hover {
    background: #3a3024;
}
QPushButton#PrimaryButton {
    background: #8a5a24;
    border-color: #b8843d;
    color: #fff4e4;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: #a06b2c;
}
QPushButton:disabled {
    color: #7c7163;
    border-color: #332b22;
    background: #1a1713;
}
QScrollArea {
    background: transparent;
}
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RoleForge — V3")
        self.resize(1200, 780)
        self.setStyleSheet(APP_STYLE)

        self.stack = QStackedWidget()
        self.home = HomeView()
        self.workshop = HeroWorkshopView()
        self.adventure = AdventureView()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.workshop)
        self.stack.addWidget(self.adventure)
        self.setCentralWidget(self.stack)

        self.home.new_requested.connect(self.show_workshop)
        self.home.open_requested.connect(self.open_campaign)
        self.home.settings_requested.connect(self.open_settings)
        self.workshop.cancelled.connect(self.show_home)
        self.workshop.created.connect(self.open_campaign)
        self.adventure.back_requested.connect(self.show_home)
        self.adventure.settings_requested.connect(self.open_settings)

    def show_home(self) -> None:
        self.home.reload()
        self.stack.setCurrentWidget(self.home)

    def show_workshop(self) -> None:
        self.stack.setCurrentWidget(self.workshop)

    def open_campaign(self, campaign_id: int) -> None:
        self.adventure.load_campaign(campaign_id)
        self.stack.setCurrentWidget(self.adventure)

    def open_settings(self) -> None:
        SettingsDialog(self).exec()
