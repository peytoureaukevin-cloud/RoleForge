from __future__ import annotations

from app.ai.fake_provider import FakeProvider
from app.ai.openai_provider import OpenAIProvider
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
        response = self.provider.generate(prompt)
        db.add_journal_entry(campaign_id, "gm", response)
        return response
