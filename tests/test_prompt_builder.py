from __future__ import annotations

from app.core.prompt_builder import build_prompt


class Row(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def keys(self):
        return dict.keys(self)


def test_prompt_contains_core_adventure_context():
    campaign = Row(name="La Tour", setting="Fantasy", summary="Un départ.")
    hero = Row(
        name="Elynn",
        origin="Orpheline",
        class_name="Rôdeuse",
        portrait_description="Regard froid.",
        traits="Patiente",
        flaws="Méfiance",
        goal="Retrouver son frère",
        strength=9,
        dexterity=14,
        intelligence=11,
        charisma=10,
        constitution=12,
        hp_current=20,
        hp_max=20,
    )
    inventory = [Row(name="Arc court", quantity=1)]
    skills = [Row(skill_name="Survie", value=4)]
    history = [Row(role="gm", content="La forêt attend.")]

    prompt = build_prompt(campaign, hero, inventory, skills, history, "J'observe.")

    assert "Elynn" in prompt
    assert "Arc court" in prompt
    assert "Survie" in prompt
    assert "J'observe." in prompt
