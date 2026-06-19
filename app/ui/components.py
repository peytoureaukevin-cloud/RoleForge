from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ChoiceCard(QFrame):
    """Reusable clickable card for RPG-style choices."""

    selected = Signal(str)

    def __init__(self, key: str, title: str, subtitle: str = "", badge: str = "") -> None:
        super().__init__()
        self.key = key
        self._selected = False
        self.setObjectName("ChoiceCard")
        self.setCursor(Qt.PointingHandCursor)

        self.badge_label = QLabel(badge)
        self.badge_label.setObjectName("CardBadge")
        self.badge_label.setAlignment(Qt.AlignRight)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setWordWrap(True)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("Muted")
        self.subtitle_label.setWordWrap(True)

        top = QHBoxLayout()
        top.addWidget(self.title_label, 1)
        if badge:
            top.addWidget(self.badge_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self.subtitle_label, 1)

    def set_selected(self, value: bool) -> None:
        self._selected = value
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):  # type: ignore[override]
        self.selected.emit(self.key)
        super().mousePressEvent(event)


class StatBar(QWidget):
    """Compact stat bar used by HeroCard and the workshop."""

    def __init__(self, label: str, value: int = 0, maximum: int = 18) -> None:
        super().__init__()
        self.maximum = maximum
        self.label = QLabel(label)
        self.label.setMinimumWidth(44)
        self.label.setObjectName("SmallCaps")
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setMinimumWidth(28)
        self.bar = QLabel()
        self.bar.setObjectName("StatBar")
        self.bar.setMinimumHeight(10)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.label)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.value_label)
        self.set_value(value)

    def set_value(self, value: int) -> None:
        value = max(0, min(self.maximum, int(value)))
        filled = round((value / self.maximum) * 12)
        self.bar.setText("█" * filled + "░" * (12 - filled))
        self.value_label.setText(str(value))


class PointAllocator(QWidget):
    """Plus/minus allocator with visual bar and spent tracking."""

    changed = Signal()

    def __init__(self, key: str, label: str, minimum: int, maximum: int, description: str = "") -> None:
        super().__init__()
        self.key = key
        self.minimum = minimum
        self.maximum = maximum
        self.value = minimum
        self.title = QLabel(label)
        self.title.setObjectName("SmallCaps")
        if description:
            self.title.setToolTip(description)
        self.minus_btn = QPushButton("−")
        self.plus_btn = QPushButton("+")
        self.minus_btn.setObjectName("TinyButton")
        self.plus_btn.setObjectName("TinyButton")
        self.stat_bar = StatBar("", minimum, maximum)
        self.stat_bar.label.hide()
        self.minus_btn.clicked.connect(self.decrease)
        self.plus_btn.clicked.connect(self.increase)

        header = QHBoxLayout()
        header.addWidget(self.title, 1)
        header.addWidget(self.minus_btn)
        header.addWidget(self.plus_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addLayout(header)
        layout.addWidget(self.stat_bar)

    def set_value(self, value: int) -> None:
        self.value = max(self.minimum, min(self.maximum, int(value)))
        self.stat_bar.set_value(self.value)
        self.changed.emit()

    def increase(self) -> None:
        self.set_value(self.value + 1)

    def decrease(self) -> None:
        self.set_value(self.value - 1)

    def spent(self) -> int:
        return self.value - self.minimum


class HeroCard(QFrame):
    """Central reusable visual summary of a hero."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("HeroCard")
        self.name = QLabel("Héros sans nom")
        self.name.setObjectName("HeroCardName")
        self.meta = QLabel("Origine · Vocation")
        self.meta.setObjectName("Muted")
        self.portrait = QLabel("◇")
        self.portrait.setObjectName("PortraitPlaceholder")
        self.portrait.setAlignment(Qt.AlignCenter)
        self.portrait.setMinimumHeight(150)

        self.goal = QLabel("Désir profond : —")
        self.goal.setObjectName("Muted")
        self.goal.setWordWrap(True)

        self.stats: dict[str, StatBar] = {
            "strength": StatBar("FOR"),
            "dexterity": StatBar("DEX"),
            "intelligence": StatBar("INT"),
            "charisma": StatBar("CHA"),
            "constitution": StatBar("CON"),
        }
        self.tags = QLabel("Traits : —")
        self.tags.setObjectName("Muted")
        self.tags.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        layout.addWidget(self.name)
        layout.addWidget(self.meta)
        layout.addWidget(self.portrait)
        layout.addWidget(self.goal)
        for stat in self.stats.values():
            layout.addWidget(stat)
        layout.addWidget(self.tags)
        layout.addStretch()

    def update_preview(
        self,
        *,
        name: str,
        origin: str,
        class_name: str,
        goal: str,
        traits: str,
        portrait: str,
        values: dict[str, int],
    ) -> None:
        self.name.setText(name.strip() or "Héros sans nom")
        self.meta.setText(f"{origin or 'Origine'} · {class_name or 'Vocation'}")
        self.goal.setText(f"Désir profond : {goal or '—'}")
        short_portrait = portrait.strip()[:120]
        self.portrait.setText(short_portrait if short_portrait else "◇\nPortrait à forger")
        for key, stat in self.stats.items():
            stat.set_value(values.get(key, 0))
        tags = ", ".join([line.strip() for line in traits.splitlines() if line.strip()][:4])
        self.tags.setText(f"Traits : {tags or '—'}")


class PillLabel(QLabel):
    """Small label used as an elegant section marker."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("PillLabel")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(28)


class InfoCard(QFrame):
    """Reusable small card with a title and optional description."""

    def __init__(self, title: str, description: str = "") -> None:
        super().__init__()
        self.setObjectName("InfoCard")
        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        description_label = QLabel(description)
        description_label.setObjectName("Muted")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        layout.addWidget(title_label)
        if description:
            layout.addWidget(description_label)
