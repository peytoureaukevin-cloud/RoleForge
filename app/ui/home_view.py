from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.database import db


class CampaignCard(QFrame):
    open_requested = Signal(int)

    def __init__(self, campaign_id: int, title: str, setting: str, updated_at: str) -> None:
        super().__init__()
        self.campaign_id = campaign_id
        self.setObjectName("CampaignCard")

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        meta = QLabel(f"{setting} · dernière activité : {updated_at}")
        meta.setObjectName("Muted")

        open_btn = QPushButton("Continuer")
        open_btn.clicked.connect(lambda: self.open_requested.emit(self.campaign_id))

        row = QHBoxLayout(self)
        text = QVBoxLayout()
        text.addWidget(title_label)
        text.addWidget(meta)
        row.addLayout(text, 1)
        row.addWidget(open_btn)


class HomeView(QWidget):
    new_requested = Signal()
    open_requested = Signal(int)
    settings_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(12)

        title = QLabel("ROLEFORGE")
        title.setObjectName("HeroTitle")
        subtitle = QLabel("Forger un héros. Vivre une aventure. Conserver la trace.")
        subtitle.setObjectName("Subtitle")

        new_btn = QPushButton("＋ Nouvelle aventure")
        settings_btn = QPushButton("Réglages IA")
        new_btn.setObjectName("PrimaryButton")
        new_btn.clicked.connect(self.new_requested.emit)
        settings_btn.clicked.connect(self.settings_requested.emit)

        actions = QHBoxLayout()
        actions.addWidget(new_btn)
        actions.addWidget(settings_btn)
        actions.addStretch()

        scroll_content = QWidget()
        scroll_content.setLayout(self.cards_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)
        scroll.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions)
        layout.addWidget(QLabel("Bibliothèque"))
        layout.addWidget(scroll, 1)

        self.reload()

    def reload(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        campaigns = db.list_campaigns()
        if not campaigns:
            empty = QLabel("Aucune aventure pour l'instant. Crée ton premier héros.")
            empty.setObjectName("Muted")
            self.cards_layout.addWidget(empty)
            self.cards_layout.addStretch()
            return

        for campaign in campaigns:
            card = CampaignCard(campaign["id"], campaign["name"], campaign["setting"], campaign["updated_at"])
            card.open_requested.connect(self.open_requested.emit)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()
