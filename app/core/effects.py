from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

EFFECTS_BLOCK_RE = re.compile(r"```roleforge_effects\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


@dataclass
class ParsedEffects:
    clean_text: str
    data: dict[str, Any] = field(default_factory=dict)


def parse_roleforge_effects(text: str) -> ParsedEffects:
    """Extract an optional structured RoleForge effects block from a GM response.

    The visible narration remains human-readable. The effects block is a private
    contract between the Conteur and the app.
    """
    match = EFFECTS_BLOCK_RE.search(text or "")
    if not match:
        return ParsedEffects(clean_text=text or "", data={})

    raw = match.group(1).strip()
    clean = (text[: match.start()] + text[match.end() :]).strip()
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            data = {}
    except json.JSONDecodeError:
        data = {}
    return ParsedEffects(clean_text=clean, data=data)


def format_effect_summary(effects: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for change in effects.get("inventory_changes", []) or []:
        if not isinstance(change, dict):
            continue
        action = change.get("action")
        name = str(change.get("name") or change.get("item") or "Objet").strip()
        qty = int(change.get("quantity") or 1)
        if action == "add":
            messages.append(f"Objet ajouté : {name} x{qty}")
        elif action == "remove":
            messages.append(f"Objet retiré : {name} x{qty}")
    for discovery in effects.get("codex_discoveries", []) or []:
        if not isinstance(discovery, dict):
            continue
        name = str(discovery.get("name") or "Découverte").strip()
        kind = str(discovery.get("kind") or "entrée").strip()
        messages.append(f"Codex mis à jour : {name} ({kind})")
    return messages
