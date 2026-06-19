from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.database import db


class SettingsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Réglages IA")
        self.setMinimumWidth(420)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Mode test sans IA", "dummy")
        self.provider_combo.addItem("OpenAI", "openai")

        current_provider = db.get_setting("ai_provider", "dummy")
        index = self.provider_combo.findData(current_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        self.api_key_input = QLineEdit(db.get_setting("openai_api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("sk-...")

        self.model_input = QLineEdit(db.get_setting("openai_model", "gpt-4.1-mini"))

        form = QFormLayout()
        form.addRow("Fournisseur", self.provider_combo)
        form.addRow("Clé OpenAI", self.api_key_input)
        form.addRow("Modèle", self.model_input)

        hint = QLabel("V1 : OpenAI est disponible. Claude, Gemini et local seront ajoutés par adaptateurs.")
        hint.setWordWrap(True)

        save_btn = QPushButton("Enregistrer")
        cancel_btn = QPushButton("Annuler")
        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addLayout(buttons)

    def save(self) -> None:
        db.set_setting("ai_provider", self.provider_combo.currentData())
        db.set_setting("openai_api_key", self.api_key_input.text().strip())
        db.set_setting("openai_model", self.model_input.text().strip() or "gpt-4.1-mini")
        self.accept()
