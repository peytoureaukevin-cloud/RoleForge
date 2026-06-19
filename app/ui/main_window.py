from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.ui.adventure_view import AdventureView
from app.ui.hero_workshop_view import HeroWorkshopView
from app.ui.home_view import HomeView
from app.ui.settings_dialog import SettingsDialog


APP_STYLE = """
QWidget {
    background: #100f0d;
    color: #f4eadb;
    font-size: 14px;
}
QLabel#HeroTitle {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 3px;
}
QLabel#Subtitle, QLabel#Muted {
    color: #b8aa96;
}
QLabel#CardTitle {
    font-size: 18px;
    font-weight: 700;
}
QLabel#HeroCardName {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 1px;
}
QLabel#SmallCaps {
    color: #d6c7b2;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#CardBadge {
    background: #352819;
    color: #d7ad6b;
    border: 1px solid #6b4a23;
    border-radius: 9px;
    padding: 3px 8px;
    font-size: 11px;
}
QLabel#PortraitPlaceholder {
    background: #181510;
    border: 1px solid #4d3923;
    border-radius: 18px;
    color: #8f6a3a;
    font-size: 18px;
    padding: 16px;
}
QLabel#StatBar {
    color: #d7ad6b;
    letter-spacing: 1px;
}
QFrame#Panel, QFrame#CampaignCard, QFrame#ChoiceCard, QFrame#HeroCard, QFrame#HeroHeader {
    background: #1b1712;
    border: 1px solid #3b2f22;
    border-radius: 18px;
}
QFrame#HeroHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22170d, stop:1 #17130f);
    border-color: #65461f;
}
QFrame#HeroCard {
    background: #17130f;
    border-color: #6b4a23;
}
QFrame#ChoiceCard:hover {
    background: #251f17;
    border-color: #8a5a24;
}
QFrame#ChoiceCard[selected="true"] {
    background: #312313;
    border: 2px solid #b8843d;
}
QRadioButton {
    spacing: 8px;
    padding: 6px;
}
QTextEdit, QLineEdit, QComboBox {
    background: #211c16;
    border: 1px solid #4a3a28;
    border-radius: 12px;
    padding: 9px;
    selection-background-color: #8f6a3a;
}
QTextEdit:focus, QLineEdit:focus, QComboBox:focus {
    border-color: #b8843d;
}
QTextEdit#Narration {
    font-size: 15px;
    line-height: 1.4;
}
QPushButton {
    background: #2b241b;
    border: 1px solid #5a4630;
    border-radius: 12px;
    padding: 9px 14px;
}
QPushButton:hover {
    background: #3a3024;
}
QPushButton#TinyButton {
    min-width: 28px;
    max-width: 34px;
    padding: 5px;
    border-radius: 9px;
}
QPushButton#PrimaryButton {
    background: #8a5a24;
    border-color: #b8843d;
    color: #fff4e4;
    font-weight: 700;
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
        self.setWindowTitle("RoleForge — Sprint 1")
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
