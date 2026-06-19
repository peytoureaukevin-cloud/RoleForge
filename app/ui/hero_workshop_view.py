from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.character_rules import (
    ATTRIBUTE_MAX,
    ATTRIBUTE_MIN,
    ATTRIBUTE_POINTS,
    CLASS_PRESETS,
    GOALS,
    ORIGINS,
    SKILL_MAX,
    SKILL_MIN,
    SKILL_POINTS,
    SKILLS,
    attribute_rows,
)
from app.database import db
from app.ui.components import ChoiceCard, HeroCard, PointAllocator

ATTRIBUTES = attribute_rows()
SETTINGS = ["Fantasy", "Space opera", "Cyberpunk", "Horreur", "Contemporain", "Univers personnalisé"]


class HeroWorkshopView(QWidget):
    created = Signal(int)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.selected_setting = SETTINGS[0]
        self.selected_origin = ORIGINS[0][0]
        self.selected_class = "Guerrier"
        self.setting_cards: dict[str, ChoiceCard] = {}
        self.origin_cards: dict[str, ChoiceCard] = {}
        self.class_cards: dict[str, ChoiceCard] = {}
        self.attribute_rows: dict[str, PointAllocator] = {}
        self.skill_rows: dict[str, PointAllocator] = {}

        self.campaign_name = QLineEdit()
        self.campaign_name.setPlaceholderText("Les Ombres de Valen")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Nom du héros")
        self.name.textChanged.connect(self.update_preview)

        self.portrait = QTextEdit()
        self.portrait.setPlaceholderText("Apparence, posture, regard, signe distinctif...")
        self.portrait.setMaximumHeight(88)
        self.portrait.textChanged.connect(self.update_preview)

        self.traits = QTextEdit()
        self.traits.setPlaceholderText("Un par ligne : loyal, curieux, patient...")
        self.traits.setMaximumHeight(74)
        self.traits.textChanged.connect(self.update_preview)

        self.flaws = QTextEdit()
        self.flaws.setPlaceholderText("Un par ligne : impulsif, méfiant, arrogant...")
        self.flaws.setMaximumHeight(74)

        self.inventory = QTextEdit()
        self.inventory.setPlaceholderText("Un objet par ligne")
        self.inventory.setMaximumHeight(86)

        self.goal_group = QButtonGroup(self)
        self.goal_buttons: list[QRadioButton] = []

        self.hero_card = HeroCard()
        self.points_label = QLabel()
        self.points_label.setObjectName("CardTitle")
        self.skill_points_label = QLabel()
        self.skill_points_label.setObjectName("CardTitle")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 28, 36, 28)
        content_layout.setSpacing(16)
        content_layout.addWidget(self._build_header())
        content_layout.addLayout(self._build_main_area(), 1)
        content_layout.addLayout(self._build_buttons())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(content)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

        self._select_setting(self.selected_setting)
        self._select_origin(self.selected_origin)
        self._select_class(self.selected_class)

    def _build_header(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("HeroHeader")
        title = QLabel("Atelier du héros")
        title.setObjectName("HeroTitle")
        subtitle = QLabel("Crée un personnage comme dans un RPG : cartes, points, vocation, désir et fiche vivante.")
        subtitle.setObjectName("Subtitle")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return frame

    def _build_main_area(self) -> QHBoxLayout:
        left = QVBoxLayout()
        left.addWidget(self._build_identity_panel())
        left.addWidget(self._build_setting_panel())
        left.addWidget(self._build_origin_panel())
        left.addWidget(self._build_class_panel())
        left.addLayout(self._build_points_area())
        left.addWidget(self._build_details_panel())

        right = QVBoxLayout()
        sticky = QFrame()
        sticky.setObjectName("Panel")
        sticky_layout = QVBoxLayout(sticky)
        sticky_layout.addWidget(QLabel("Fiche vivante"))
        sticky_layout.addWidget(self.hero_card, 1)
        right.addWidget(sticky)
        right.addStretch()

        main = QHBoxLayout()
        main.setSpacing(16)
        main.addLayout(left, 3)
        main.addLayout(right, 1)
        return main

    def _build_identity_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QGridLayout(panel)
        layout.addWidget(QLabel("Campagne"), 0, 0)
        layout.addWidget(self.campaign_name, 0, 1)
        layout.addWidget(QLabel("Nom du héros"), 1, 0)
        layout.addWidget(self.name, 1, 1)
        layout.addWidget(QLabel("Portrait textuel"), 2, 0)
        layout.addWidget(self.portrait, 2, 1)
        return panel

    def _build_setting_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("1. Choisir le ton de l'aventure"))
        cards = QGridLayout()
        for i, setting in enumerate(SETTINGS):
            card = ChoiceCard(setting, setting, "Base d'ambiance de la campagne.", "Monde")
            card.selected.connect(self._select_setting)
            self.setting_cards[setting] = card
            cards.addWidget(card, i // 3, i % 3)
        layout.addLayout(cards)
        return panel

    def _build_origin_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("2. Choisir une origine"))
        cards = QGridLayout()
        for i, (origin, subtitle, badge) in enumerate(ORIGINS):
            card = ChoiceCard(origin, origin, subtitle, badge)
            card.selected.connect(self._select_origin)
            self.origin_cards[origin] = card
            cards.addWidget(card, i // 3, i % 3)
        layout.addLayout(cards)
        return panel

    def _build_class_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("3. Choisir une vocation"))
        cards = QGridLayout()
        for i, (class_name, preset) in enumerate(CLASS_PRESETS.items()):
            card = ChoiceCard(class_name, class_name, preset.get("pitch", ""), "Vocation")
            card.selected.connect(self._select_class)
            self.class_cards[class_name] = card
            cards.addWidget(card, i // 3, i % 3)
        layout.addLayout(cards)
        return panel

    def _build_points_area(self) -> QHBoxLayout:
        stats = QFrame()
        stats.setObjectName("Panel")
        stats_layout = QVBoxLayout(stats)
        stats_layout.addWidget(self.points_label)
        for key, label, description in ATTRIBUTES:
            row = PointAllocator(key, label, ATTRIBUTE_MIN, ATTRIBUTE_MAX, description)
            row.changed.connect(self.update_points)
            self.attribute_rows[key] = row
            stats_layout.addWidget(row)
        stats_layout.addStretch()

        skills = QFrame()
        skills.setObjectName("Panel")
        skills_layout = QVBoxLayout(skills)
        skills_layout.addWidget(self.skill_points_label)
        for key, label in SKILLS:
            row = PointAllocator(key, label, SKILL_MIN, SKILL_MAX)
            row.changed.connect(self.update_points)
            self.skill_rows[key] = row
            skills_layout.addWidget(row)
        skills_layout.addStretch()

        goals = QFrame()
        goals.setObjectName("Panel")
        goals_layout = QVBoxLayout(goals)
        goals_layout.addWidget(QLabel("4. Désir profond"))
        for i, goal in enumerate(GOALS):
            btn = QRadioButton(goal)
            if i == 0:
                btn.setChecked(True)
            btn.toggled.connect(self.update_preview)
            self.goal_group.addButton(btn)
            self.goal_buttons.append(btn)
            goals_layout.addWidget(btn)
        goals_layout.addStretch()

        row = QHBoxLayout()
        row.addWidget(stats, 1)
        row.addWidget(skills, 1)
        row.addWidget(goals, 1)
        return row

    def _build_details_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QGridLayout(panel)
        layout.addWidget(QLabel("Traits"), 0, 0)
        layout.addWidget(self.traits, 0, 1)
        layout.addWidget(QLabel("Défauts"), 1, 0)
        layout.addWidget(self.flaws, 1, 1)
        layout.addWidget(QLabel("Inventaire"), 2, 0)
        layout.addWidget(self.inventory, 2, 1)
        return panel

    def _build_buttons(self) -> QHBoxLayout:
        cancel_btn = QPushButton("Retour")
        create_btn = QPushButton("Forger le héros")
        create_btn.setObjectName("PrimaryButton")
        cancel_btn.clicked.connect(self.cancelled.emit)
        create_btn.clicked.connect(self.create)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(create_btn)
        return buttons

    def _select_setting(self, setting: str) -> None:
        self.selected_setting = setting
        for key, card in self.setting_cards.items():
            card.set_selected(key == setting)
        self.update_preview()

    def _select_origin(self, origin: str) -> None:
        self.selected_origin = origin
        for key, card in self.origin_cards.items():
            card.set_selected(key == origin)
        self.update_preview()

    def _select_class(self, class_name: str) -> None:
        self.selected_class = class_name
        for key, card in self.class_cards.items():
            card.set_selected(key == class_name)
        self.apply_class_preset(class_name)
        self.update_preview()

    def apply_class_preset(self, class_name: str) -> None:
        preset = CLASS_PRESETS.get(class_name)
        if not preset:
            return
        for key, value in preset["attrs"].items():
            self.attribute_rows[key].set_value(value)
        for key, value in preset["skills"].items():
            self.skill_rows[key].set_value(value)
        self.inventory.setPlainText(preset["inventory"])
        self.update_points()

    def selected_goal(self) -> str:
        return next((btn.text() for btn in self.goal_buttons if btn.isChecked()), "")

    def current_attribute_values(self) -> dict[str, int]:
        return {key: row.value for key, row in self.attribute_rows.items()}

    def update_points(self) -> None:
        attr_spent = sum(row.spent() for row in self.attribute_rows.values())
        attr_remaining = ATTRIBUTE_POINTS - attr_spent
        skill_spent = sum(row.spent() for row in self.skill_rows.values())
        skill_remaining = SKILL_POINTS - skill_spent
        self.points_label.setText(f"5. Attributs — points restants : {attr_remaining}")
        self.skill_points_label.setText(f"6. Compétences — points restants : {skill_remaining}")
        for row in self.attribute_rows.values():
            row.plus_btn.setEnabled(attr_remaining > 0 and row.value < row.maximum)
            row.minus_btn.setEnabled(row.value > row.minimum)
        for row in self.skill_rows.values():
            row.plus_btn.setEnabled(skill_remaining > 0 and row.value < row.maximum)
            row.minus_btn.setEnabled(row.value > row.minimum)
        self.update_preview()

    def update_preview(self) -> None:
        if not hasattr(self, "hero_card"):
            return
        self.hero_card.update_preview(
            name=self.name.text(),
            origin=self.selected_origin,
            class_name=self.selected_class,
            goal=self.selected_goal(),
            traits=self.traits.toPlainText(),
            portrait=self.portrait.toPlainText(),
            values=self.current_attribute_values(),
        )

    def create(self) -> None:
        campaign_name = self.campaign_name.text().strip()
        hero_name = self.name.text().strip()
        attr_remaining = ATTRIBUTE_POINTS - sum(row.spent() for row in self.attribute_rows.values())
        skill_remaining = SKILL_POINTS - sum(row.spent() for row in self.skill_rows.values())
        if not campaign_name:
            QMessageBox.warning(self, "Campagne", "Donne un nom à la campagne.")
            return
        if not hero_name:
            QMessageBox.warning(self, "Héros", "Donne un nom au héros.")
            return
        if attr_remaining != 0:
            QMessageBox.warning(self, "Attributs", f"Répartis exactement les {ATTRIBUTE_POINTS} points d'attributs.")
            return
        if skill_remaining != 0:
            QMessageBox.warning(self, "Compétences", f"Répartis exactement les {SKILL_POINTS} points de compétences.")
            return

        campaign_id = db.create_campaign(campaign_name, self.selected_setting)
        selected_goal = self.selected_goal()
        hero = {
            "name": hero_name,
            "origin": self.selected_origin,
            "class_name": self.selected_class,
            "portrait_description": self.portrait.toPlainText().strip(),
            "traits": self.traits.toPlainText().strip(),
            "flaws": self.flaws.toPlainText().strip(),
            "goal": selected_goal,
        }
        for key, _label, _description in ATTRIBUTES:
            hero[key] = self.attribute_rows[key].value
        skills = [(key, label, self.skill_rows[key].value) for key, label in SKILLS]
        inventory = self.inventory.toPlainText().splitlines()
        db.create_hero(campaign_id, hero, inventory, skills)
        db.add_journal_entry(campaign_id, "system", f"{hero_name} entre dans la légende. Désir profond : {selected_goal}.")
        self.created.emit(campaign_id)
