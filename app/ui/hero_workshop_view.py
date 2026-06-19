from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import db


from app.core.character_rules import (
    ATTRIBUTE_MAX,
    ATTRIBUTE_MIN,
    ATTRIBUTE_POINTS,
    CLASS_PRESETS,
    GOALS,
    SKILL_MAX,
    SKILL_MIN,
    SKILL_POINTS,
    SKILLS,
    attribute_rows,
    validate_exact_pool,
)

ATTRIBUTES = attribute_rows()


class PointRow(QWidget):
    changed = Signal()

    def __init__(self, key: str, label: str, minimum: int, maximum: int, description: str = "") -> None:
        super().__init__()
        self.key = key
        self.minimum = minimum
        self.maximum = maximum
        self.value = minimum
        self.name_label = QLabel(label)
        self.name_label.setMinimumWidth(120)
        self.value_label = QLabel(str(self.value))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setMinimumWidth(34)
        self.minus_btn = QPushButton("−")
        self.plus_btn = QPushButton("+")
        self.minus_btn.clicked.connect(self.decrease)
        self.plus_btn.clicked.connect(self.increase)
        if description:
            self.name_label.setToolTip(description)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.name_label, 1)
        layout.addWidget(self.minus_btn)
        layout.addWidget(self.value_label)
        layout.addWidget(self.plus_btn)

    def set_value(self, value: int) -> None:
        self.value = max(self.minimum, min(self.maximum, value))
        self.value_label.setText(str(self.value))
        self.changed.emit()

    def increase(self) -> None:
        self.set_value(self.value + 1)

    def decrease(self) -> None:
        self.set_value(self.value - 1)

    def spent(self) -> int:
        return self.value - self.minimum


class ChoiceCard(QFrame):
    clicked = Signal(str)

    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        self.title = title
        self.setObjectName("ChoiceCard")
        self.setCursor(Qt.PointingHandCursor)
        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("Muted")
        subtitle_label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

    def mousePressEvent(self, event):  # type: ignore[override]
        self.clicked.emit(self.title)
        super().mousePressEvent(event)


class HeroWorkshopView(QWidget):
    created = Signal(int)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.attribute_rows: dict[str, PointRow] = {}
        self.skill_rows: dict[str, PointRow] = {}

        self.campaign_name = QLineEdit()
        self.campaign_name.setPlaceholderText("Les Ombres de Valen")
        self.setting = QComboBox()
        self.setting.addItems(["Fantasy", "Space opera", "Cyberpunk", "Horreur", "Contemporain", "Univers personnalisé"])

        self.name = QLineEdit()
        self.name.setPlaceholderText("Nom du héros")
        self.origin = QComboBox()
        self.origin.addItems(["Humain", "Elfe", "Nain", "Orphelin", "Exilé", "Synthétique", "Personnalisé"])
        self.class_name = QComboBox()
        self.class_name.addItems(["Guerrier", "Rôdeur", "Mage", "Voleur", "Diplomate", "Contrebandier", "Libre"])
        self.class_name.currentTextChanged.connect(self.apply_class_preset)

        self.goal_group = QButtonGroup(self)
        self.goal_buttons: list[QRadioButton] = []
        goals = GOALS
        goal_panel = QFrame()
        goal_panel.setObjectName("Panel")
        goal_layout = QVBoxLayout(goal_panel)
        goal_layout.addWidget(QLabel("Désir profond"))
        for i, goal in enumerate(goals):
            btn = QRadioButton(goal)
            if i == 0:
                btn.setChecked(True)
            self.goal_group.addButton(btn)
            self.goal_buttons.append(btn)
            goal_layout.addWidget(btn)

        self.portrait = QTextEdit()
        self.portrait.setPlaceholderText("Apparence, posture, regard, signe distinctif...")
        self.portrait.setMaximumHeight(76)
        self.traits = QTextEdit()
        self.traits.setPlaceholderText("Un par ligne : loyal, curieux, patient...")
        self.traits.setMaximumHeight(74)
        self.flaws = QTextEdit()
        self.flaws.setPlaceholderText("Un par ligne : impulsif, méfiant, arrogant...")
        self.flaws.setMaximumHeight(74)
        self.inventory = QTextEdit()
        self.inventory.setPlaceholderText("Un objet par ligne")
        self.inventory.setMaximumHeight(86)

        title = QLabel("Atelier du héros")
        title.setObjectName("HeroTitle")
        subtitle = QLabel("On ne remplit pas une fiche : on forge un personnage jouable.")
        subtitle.setObjectName("Subtitle")

        identity = QFrame()
        identity.setObjectName("Panel")
        identity_layout = QGridLayout(identity)
        identity_layout.addWidget(QLabel("Campagne"), 0, 0)
        identity_layout.addWidget(self.campaign_name, 0, 1)
        identity_layout.addWidget(QLabel("Univers"), 0, 2)
        identity_layout.addWidget(self.setting, 0, 3)
        identity_layout.addWidget(QLabel("Nom"), 1, 0)
        identity_layout.addWidget(self.name, 1, 1)
        identity_layout.addWidget(QLabel("Origine"), 1, 2)
        identity_layout.addWidget(self.origin, 1, 3)
        identity_layout.addWidget(QLabel("Classe"), 2, 0)
        identity_layout.addWidget(self.class_name, 2, 1)
        identity_layout.addWidget(QLabel("Portrait"), 3, 0)
        identity_layout.addWidget(self.portrait, 3, 1, 1, 3)

        presets = QFrame()
        presets.setObjectName("Panel")
        presets_layout = QVBoxLayout(presets)
        presets_layout.addWidget(QLabel("Archétypes rapides"))
        cards = QHBoxLayout()
        for title_, subtitle_ in [
            ("Guerrier", "Encaisser, frapper, tenir la ligne."),
            ("Rôdeur", "Observer, survivre, frapper juste."),
            ("Mage", "Comprendre, manipuler, révéler."),
            ("Contrebandier", "Improviser, mentir, disparaître."),
        ]:
            card = ChoiceCard(title_, subtitle_)
            card.clicked.connect(lambda value, self=self: self.class_name.setCurrentText(value))
            cards.addWidget(card)
        presets_layout.addLayout(cards)

        stats = QFrame()
        stats.setObjectName("Panel")
        stats_layout = QVBoxLayout(stats)
        self.points_label = QLabel()
        self.points_label.setObjectName("CardTitle")
        stats_layout.addWidget(self.points_label)
        for key, label, description in ATTRIBUTES:
            row = PointRow(key, label, ATTRIBUTE_MIN, ATTRIBUTE_MAX, description)
            row.changed.connect(self.update_points)
            self.attribute_rows[key] = row
            stats_layout.addWidget(row)
        stats_layout.addStretch()

        skills = QFrame()
        skills.setObjectName("Panel")
        skills_layout = QVBoxLayout(skills)
        self.skill_points_label = QLabel()
        self.skill_points_label.setObjectName("CardTitle")
        skills_layout.addWidget(self.skill_points_label)
        for key, label in SKILLS:
            row = PointRow(key, label, SKILL_MIN, SKILL_MAX)
            row.changed.connect(self.update_points)
            self.skill_rows[key] = row
            skills_layout.addWidget(row)
        skills_layout.addStretch()

        details = QFrame()
        details.setObjectName("Panel")
        details_layout = QGridLayout(details)
        details_layout.addWidget(QLabel("Traits"), 0, 0)
        details_layout.addWidget(self.traits, 0, 1)
        details_layout.addWidget(QLabel("Défauts"), 1, 0)
        details_layout.addWidget(self.flaws, 1, 1)
        details_layout.addWidget(QLabel("Inventaire"), 2, 0)
        details_layout.addWidget(self.inventory, 2, 1)

        cancel_btn = QPushButton("Retour")
        create_btn = QPushButton("Forger le héros")
        create_btn.setObjectName("PrimaryButton")
        cancel_btn.clicked.connect(self.cancelled.emit)
        create_btn.clicked.connect(self.create)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(create_btn)

        center = QHBoxLayout()
        center.addWidget(stats, 1)
        center.addWidget(skills, 1)
        center.addWidget(goal_panel, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(identity)
        layout.addWidget(presets)
        layout.addLayout(center, 1)
        layout.addWidget(details)
        layout.addLayout(buttons)
        self.apply_class_preset(self.class_name.currentText())

    def apply_class_preset(self, class_name: str) -> None:
        preset = CLASS_PRESETS.get(class_name)
        if not preset:
            return
        for key, value in preset["attrs"].items():
            self.attribute_rows[key].set_value(value)
        for key, value in preset["skills"].items():
            self.skill_rows[key].set_value(value)
        if not self.inventory.toPlainText().strip():
            self.inventory.setPlainText(preset["inventory"])
        self.update_points()

    def update_points(self) -> None:
        attr_spent = sum(row.spent() for row in self.attribute_rows.values())
        attr_remaining = ATTRIBUTE_POINTS - attr_spent
        skill_spent = sum(row.spent() for row in self.skill_rows.values())
        skill_remaining = SKILL_POINTS - skill_spent
        self.points_label.setText(f"Attributs — points restants : {attr_remaining}")
        self.skill_points_label.setText(f"Compétences — points restants : {skill_remaining}")
        for row in self.attribute_rows.values():
            row.plus_btn.setEnabled(attr_remaining > 0 and row.value < row.maximum)
            row.minus_btn.setEnabled(row.value > row.minimum)
        for row in self.skill_rows.values():
            row.plus_btn.setEnabled(skill_remaining > 0 and row.value < row.maximum)
            row.minus_btn.setEnabled(row.value > row.minimum)

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

        campaign_id = db.create_campaign(campaign_name, self.setting.currentText())
        selected_goal = next((btn.text() for btn in self.goal_buttons if btn.isChecked()), "")
        hero = {
            "name": hero_name,
            "origin": self.origin.currentText(),
            "class_name": self.class_name.currentText(),
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
