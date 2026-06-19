from __future__ import annotations

from html import escape

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.dice import roll
from app.core.game_engine import GameEngine
from app.database import db
from app.ui.components import HeroCard, InfoCard, PillLabel


ACTION_PRESETS = [
    ("Observer", "J'observe attentivement les lieux avant d'agir."),
    ("Écouter", "Je reste silencieux et j'écoute ce qui se passe autour de moi."),
    ("Parler", "Je tente d'engager la conversation sans provoquer de conflit."),
    ("Discrétion", "J'avance prudemment en essayant de ne pas me faire remarquer."),
    ("Inventaire", "Je vérifie mon équipement et cherche ce qui peut m'aider."),
    ("Intuition", "Je prends un instant pour comprendre ce qui cloche dans la situation."),
]


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

        self.narration = QTextBrowser()
        self.narration.setOpenExternalLinks(False)
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

        quick_grid = QGridLayout()
        quick_grid.setHorizontalSpacing(8)
        quick_grid.setVerticalSpacing(8)
        for index, (label, action) in enumerate(ACTION_PRESETS):
            btn = QPushButton(label)
            btn.setObjectName("ActionButton")
            btn.clicked.connect(lambda _checked=False, text=action: self.set_quick_action(text))
            quick_grid.addWidget(btn, index // 3, index % 3)

        self.hero_card = HeroCard()
        self.hero_card.setMaximumWidth(390)

        self.inventory_panel = QTextEdit()
        self.inventory_panel.setReadOnly(True)
        self.inventory_panel.setObjectName("PanelText")

        self.campaign_panel = QTextEdit()
        self.campaign_panel.setReadOnly(True)
        self.campaign_panel.setObjectName("PanelText")

        self.codex_panel = QTextEdit()
        self.codex_panel.setReadOnly(True)
        self.codex_panel.setObjectName("PanelText")

        self.last_roll = QLabel("Aucun jet lancé.")
        self.last_roll.setObjectName("Muted")

        d20_btn = QPushButton("🎲 Lancer D20")
        d20_btn.clicked.connect(self.roll_d20)
        settings_btn = QPushButton("Réglages IA")
        settings_btn.clicked.connect(self.settings_requested.emit)
        back_btn = QPushButton("Bibliothèque")
        back_btn.clicked.connect(self.back_requested.emit)

        dice_card = InfoCard("Dés", "Lancez un D20 et conservez le résultat dans le journal.")
        dice_card.layout().addWidget(self.last_roll)  # type: ignore[union-attr]
        dice_card.layout().addWidget(d20_btn)  # type: ignore[union-attr]

        side_tabs = QTabWidget()
        side_tabs.setObjectName("SideTabs")
        side_tabs.addTab(self.hero_card, "Héros")
        side_tabs.addTab(self.inventory_panel, "Sac")
        side_tabs.addTab(self.codex_panel, "Codex")
        side_tabs.addTab(self.campaign_panel, "Journal")

        side = QFrame()
        side.setObjectName("Panel")
        side.setMaximumWidth(430)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(14, 14, 14, 14)
        side_layout.setSpacing(12)
        side_layout.addWidget(side_tabs, 1)
        side_layout.addWidget(dice_card)
        side_layout.addWidget(settings_btn)
        side_layout.addWidget(back_btn)

        adventure_card = QFrame()
        adventure_card.setObjectName("AdventurePanel")
        adventure_layout = QVBoxLayout(adventure_card)
        adventure_layout.setContentsMargins(18, 18, 18, 18)
        adventure_layout.setSpacing(12)
        adventure_layout.addWidget(PillLabel("Aventure en cours"))
        adventure_layout.addWidget(self.narration, 1)
        adventure_layout.addLayout(input_row)
        adventure_layout.addLayout(quick_grid)

        main = QHBoxLayout()
        main.setSpacing(18)
        main.addWidget(adventure_card, 3)
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
            self.subtitle.setText(f"Univers : {campaign['setting']} · Le conteur conserve chaque trace.")
        self.refresh()

    def refresh(self) -> None:
        if self.campaign_id is None:
            return
        entries = db.all_journal(self.campaign_id)
        self.narration.setHtml(self._render_journal_html(entries))
        self.narration.verticalScrollBar().setValue(self.narration.verticalScrollBar().maximum())
        self.refresh_side_panels()

    def _render_journal_html(self, entries) -> str:
        if not entries:
            return """
            <div class='empty'>
                <h2>La première page est encore blanche.</h2>
                <p>Écrivez une action ou choisissez une intention rapide pour faire entrer votre héros dans l'histoire.</p>
            </div>
            """

        rows: list[str] = []
        for entry in entries:
            role = entry["role"]
            if role == "player":
                label = "Vous"
                css = "player"
            elif role == "gm":
                label = "Conteur"
                css = "gm"
            else:
                label = "Système"
                css = "system"
            content = escape(entry["content"]).replace("\n", "<br>")
            rows.append(f"<article class='entry {css}'><div class='speaker'>{label}</div><p>{content}</p></article>")

        style = """
        <style>
        body { background: #17130f; color: #f4eadb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI'; }
        .entry { border: 1px solid #3b2f22; border-radius: 16px; padding: 14px 16px; margin: 0 0 14px 0; background: #211c16; }
        .entry.player { border-color: #5a4630; background: #241f18; }
        .entry.gm { border-color: #6b4a23; background: #1d1710; }
        .entry.system { border-color: #40382d; background: #191713; color: #c7b8a3; }
        .speaker { color: #d7ad6b; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; font-size: 11px; margin-bottom: 7px; }
        p { margin: 0; line-height: 1.45; font-size: 15px; }
        .empty { padding: 34px; color: #b8aa96; }
        .empty h2 { color: #f4eadb; }
        </style>
        """
        return style + "".join(rows)

    def refresh_side_panels(self) -> None:
        if self.campaign_id is None:
            return
        campaign = db.get_campaign(self.campaign_id)
        hero = db.get_hero(self.campaign_id)
        if hero is None:
            self.inventory_panel.setPlainText("Aucun héros.")
            self.campaign_panel.setPlainText("Aucun journal.")
            return

        inventory = db.get_inventory(hero["id"])
        skills = db.get_skills(hero["id"])
        values = {
            "strength": hero["strength"],
            "dexterity": hero["dexterity"],
            "intelligence": hero["intelligence"],
            "charisma": hero["charisma"],
            "constitution": hero["constitution"],
        }
        self.hero_card.update_preview(
            name=hero["name"],
            origin=hero["origin"],
            class_name=hero["class_name"],
            goal=hero["goal"] if "goal" in hero.keys() else "",
            traits=hero["traits"] or "",
            portrait=hero["portrait_description"] or "",
            values=values,
        )

        inventory_text = "\n".join(f"• {item['name']} x{item['quantity']}" for item in inventory) or "Aucun objet."
        skills_text = "\n".join(f"• {skill['skill_name']} : {skill['value']}/5" for skill in skills) or "Aucune spécialisation."
        self.inventory_panel.setPlainText(
            f"PV\n{hero['hp_current']}/{hero['hp_max']}\n\n"
            f"Compétences\n{skills_text}\n\n"
            f"Inventaire\n{inventory_text}\n\n"
            f"Défauts\n{hero['flaws'] or '-'}"
        )

        entries_count = len(db.all_journal(self.campaign_id))
        summary = campaign["summary"] if campaign and campaign["summary"] else "La campagne commence."
        self.campaign_panel.setPlainText(
            f"Résumé\n{summary}\n\n"
            f"Entrées de journal\n{entries_count}\n\n"
            "Règle de V2\nChaque action du joueur et chaque réponse du conteur deviennent une trace persistante."
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
        label = "échec critique" if value == 1 else "réussite critique" if value == 20 else "résultat"
        self.last_roll.setText(f"Dernier jet : {value} · {label}")
        db.add_journal_entry(self.campaign_id, "system", f"Jet de D20 : {value} ({label})")
        self.refresh()
