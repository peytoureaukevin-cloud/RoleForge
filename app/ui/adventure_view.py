from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.dice import roll
from app.core.game_engine import GameEngine
from app.database import db


class AdventureView(QWidget):
    back_requested = Signal()
    settings_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.campaign_id: int | None = None

        self.title = QLabel("Salle d'aventure")
        self.title.setObjectName("HeroTitle")
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("Subtitle")

        self.narration = QTextEdit()
        self.narration.setReadOnly(True)
        self.narration.setObjectName("Narration")

        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("Que faites-vous ?")
        self.action_input.returnPressed.connect(self.send_action)
        send_btn = QPushButton("Envoyer")
        send_btn.setObjectName("PrimaryButton")
        send_btn.clicked.connect(self.send_action)

        input_row = QHBoxLayout()
        input_row.addWidget(self.action_input, 1)
        input_row.addWidget(send_btn)

        quick_row = QHBoxLayout()
        for label, action in [
            ("Observer", "J'observe attentivement les lieux avant d'agir."),
            ("Parler", "Je tente d'engager la conversation."),
            ("Discrétion", "J'avance prudemment en essayant de ne pas me faire remarquer."),
            ("Inventaire", "Je vérifie mon équipement et cherche ce qui peut m'aider."),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _checked=False, text=action: self.set_quick_action(text))
            quick_row.addWidget(btn)
        quick_row.addStretch()

        self.hero_panel = QTextEdit()
        self.hero_panel.setReadOnly(True)
        self.hero_panel.setObjectName("PanelText")
        self.hero_panel.setMaximumWidth(360)

        d20_btn = QPushButton("🎲 Lancer D20")
        d20_btn.clicked.connect(self.roll_d20)
        settings_btn = QPushButton("Réglages IA")
        settings_btn.clicked.connect(self.settings_requested.emit)
        back_btn = QPushButton("Bibliothèque")
        back_btn.clicked.connect(self.back_requested.emit)

        side = QFrame()
        side.setObjectName("Panel")
        side_layout = QVBoxLayout(side)
        side_layout.addWidget(QLabel("Héros"))
        side_layout.addWidget(self.hero_panel, 1)
        side_layout.addWidget(d20_btn)
        side_layout.addWidget(settings_btn)
        side_layout.addWidget(back_btn)

        main = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(self.narration, 1)
        left.addLayout(input_row)
        left.addLayout(quick_row)
        main.addLayout(left, 3)
        main.addWidget(side, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(14)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addLayout(main, 1)

    def load_campaign(self, campaign_id: int) -> None:
        self.campaign_id = campaign_id
        campaign = db.get_campaign(campaign_id)
        if campaign:
            self.title.setText(campaign["name"])
            self.subtitle.setText(f"Univers : {campaign['setting']}")
        self.refresh()

    def refresh(self) -> None:
        if self.campaign_id is None:
            return
        entries = db.all_journal(self.campaign_id)
        blocks = []
        for entry in entries:
            if entry["role"] == "player":
                speaker = "Vous"
            elif entry["role"] == "gm":
                speaker = "Conteur"
            else:
                speaker = "Système"
            blocks.append(f"{speaker}\n{entry['content']}")
        self.narration.setPlainText("\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(blocks))
        self.narration.verticalScrollBar().setValue(self.narration.verticalScrollBar().maximum())
        self.refresh_hero_panel()

    def refresh_hero_panel(self) -> None:
        if self.campaign_id is None:
            return
        hero = db.get_hero(self.campaign_id)
        if hero is None:
            self.hero_panel.setPlainText("Aucun héros.")
            return
        inventory = db.get_inventory(hero["id"])
        skills = db.get_skills(hero["id"])
        inventory_text = "\n".join(f"• {item['name']} x{item['quantity']}" for item in inventory) or "Aucun objet."
        skills_text = "\n".join(f"• {skill['skill_name']} : {skill['value']}/5" for skill in skills) or "Aucune spécialisation."
        goal = hero['goal'] if 'goal' in hero.keys() else ''
        self.hero_panel.setPlainText(
            f"{hero['name']}\n"
            f"{hero['origin']} · {hero['class_name']}\n\n"
            f"PV : {hero['hp_current']}/{hero['hp_max']}\n\n"
            f"Force : {hero['strength']}\n"
            f"Dextérité : {hero['dexterity']}\n"
            f"Intelligence : {hero['intelligence']}\n"
            f"Charisme : {hero['charisma']}\n"
            f"Constitution : {hero['constitution']}\n\n"
            f"Désir profond :\n{goal or '-'}\n\n"
            f"Compétences :\n{skills_text}\n\n"
            f"Traits :\n{hero['traits'] or '-'}\n\n"
            f"Défauts :\n{hero['flaws'] or '-'}\n\n"
            f"Inventaire :\n{inventory_text}"
        )

    def set_quick_action(self, text: str) -> None:
        self.action_input.setText(text)
        self.action_input.setFocus()

    def send_action(self) -> None:
        if self.campaign_id is None:
            return
        action = self.action_input.text().strip()
        if not action:
            return
        self.action_input.clear()
        try:
            GameEngine().play_turn(self.campaign_id, action)
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))
        self.refresh()

    def roll_d20(self) -> None:
        if self.campaign_id is None:
            return
        value = roll(20)
        db.add_journal_entry(self.campaign_id, "system", f"Jet de D20 : {value}")
        self.refresh()
