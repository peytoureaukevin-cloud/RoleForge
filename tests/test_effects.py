from app.core.effects import format_effect_summary, parse_roleforge_effects


def test_parse_roleforge_effects_extracts_private_block():
    text = '''Narration visible.

```roleforge_effects
{"inventory_changes":[{"action":"add","name":"Clé ancienne","quantity":1}],"codex_discoveries":[{"kind":"objet","name":"Clé ancienne"}]}
```'''
    parsed = parse_roleforge_effects(text)

    assert parsed.clean_text == "Narration visible."
    assert parsed.data["inventory_changes"][0]["name"] == "Clé ancienne"


def test_format_effect_summary_for_inventory_and_codex():
    messages = format_effect_summary(
        {
            "inventory_changes": [{"action": "add", "name": "Fiole", "quantity": 2}],
            "codex_discoveries": [{"kind": "objet", "name": "Fiole"}],
        }
    )

    assert "Objet ajouté : Fiole x2" in messages
    assert "Codex mis à jour : Fiole (objet)" in messages
