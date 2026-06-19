from __future__ import annotations

from app.ai.fake_provider import FakeProvider
from app.ai.openai_provider import OpenAIProvider
from app.core.effects import format_effect_summary, parse_roleforge_effects
from app.core.prompt_builder import build_prompt
from app.database import db


class GameEngine:
    def __init__(self) -> None:
        provider_name = db.get_setting("ai_provider", "fake")
        api_key = db.get_setting("openai_api_key", "")
        model = db.get_setting("openai_model", "gpt-4.1-mini")

        if provider_name == "openai" and api_key.strip():
            self.provider = OpenAIProvider(api_key=api_key.strip(), model=model)
        else:
            self.provider = FakeProvider()

    def play_turn(self, campaign_id: int, player_action: str) -> str:
        campaign = db.get_campaign(campaign_id)
        hero = db.get_hero(campaign_id)
        if campaign is None:
            raise RuntimeError("Campagne introuvable.")
        if hero is None:
            raise RuntimeError("Crée d'abord un héros pour cette campagne.")

        inventory = db.get_inventory(hero["id"])
        skills = db.get_skills(hero["id"])
        history = db.recent_journal(campaign_id, limit=12)
        prompt = build_prompt(campaign, hero, inventory, skills, history, player_action)

        db.add_journal_entry(campaign_id, "player", player_action)
        raw_response = self.provider.generate(prompt)
        parsed = parse_roleforge_effects(raw_response)
        self._apply_effects(campaign_id, hero["id"], parsed.data)
        db.add_journal_entry(campaign_id, "gm", parsed.clean_text)

        for message in format_effect_summary(parsed.data):
            db.add_journal_entry(campaign_id, "system", message)

        return parsed.clean_text

    def _apply_effects(self, campaign_id: int, hero_id: int, effects: dict) -> None:
        for change in effects.get("inventory_changes", []) or []:
            if not isinstance(change, dict):
                continue
            action = change.get("action")
            name = str(change.get("name") or change.get("item") or "").strip()
            description = str(change.get("description") or "")
            quantity = int(change.get("quantity") or 1)
            rarity = str(change.get("rarity") or "commun")
            if action == "add":
                db.add_inventory_item(hero_id, name, description, quantity, rarity, source="conteur")
            elif action == "remove":
                db.remove_inventory_item(hero_id, name, quantity)

        for discovery in effects.get("codex_discoveries", []) or []:
            if not isinstance(discovery, dict):
                continue
            db.add_codex_entry(
                campaign_id,
                kind=str(discovery.get("kind") or "entrée"),
                name=str(discovery.get("name") or ""),
                description=str(discovery.get("description") or ""),
                source="conteur",
            )
