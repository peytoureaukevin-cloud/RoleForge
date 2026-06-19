from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout

from app.database import db


class CampaignDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nouvelle campagne")
        self.setMinimumWidth(500)
        self.created_campaign_id: int | None = None

        self.campaign_name = QLineEdit("Les Ombres de la Bordure")
        self.setting = QLineEdit("Space opera sombre, contrebandiers, ruines anciennes, pouvoirs oubliés")
        self.character_name = QLineEdit("Kael Venn")
        self.archetype = QLineEdit("Contrebandier sensible à une force ancienne")
        self.description = QTextEdit("Prudent, ironique, débrouillard. Il ignore encore l'origine exacte de ses intuitions.")
        self.description.setFixedHeight(90)

        form = QFormLayout()
        form.addRow("Nom campagne", self.campaign_name)
        form.addRow("Univers", self.setting)
        form.addRow("Nom personnage", self.character_name)
        form.addRow("Archétype", self.archetype)
        form.addRow("Description", self.description)

        create_btn = QPushButton("Créer")
        cancel_btn = QPushButton("Annuler")
        create_btn.clicked.connect(self.create)
        cancel_btn.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(create_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def create(self) -> None:
        campaign_id = db.create_campaign(
            self.campaign_name.text().strip() or "Campagne sans titre",
            self.setting.text().strip(),
        )
        db.create_character(
            campaign_id=campaign_id,
            name=self.character_name.text().strip() or "Personnage sans nom",
            archetype=self.archetype.text().strip(),
            description=self.description.toPlainText().strip(),
        )
        db.add_journal_entry(campaign_id, "system", "Campagne créée.")
        self.created_campaign_id = campaign_id
        self.accept()
