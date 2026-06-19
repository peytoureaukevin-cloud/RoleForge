from __future__ import annotations

from app.ai.base_provider import AIProvider


class FakeProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        lower = prompt.lower()
        effects = ""
        if any(word in lower for word in ["je prends", "je ramasse", "je fouille", "je récupère"]):
            effects = '''

```roleforge_effects
{"inventory_changes":[{"action":"add","name":"Fragment de métal gravé","description":"Un petit fragment froid, marqué d'un symbole encore incompréhensible.","quantity":1,"rarity":"inhabituel"}],"codex_discoveries":[{"kind":"objet","name":"Fragment de métal gravé","description":"Premier objet ajouté automatiquement par le Conteur de test."}]}
```'''

        return (
            "Le conteur de test se penche sur la scène.\n\n"
            "Votre action est prise en compte. Le monde réagit encore simplement pour l'instant, "
            "mais une règle importante est déjà active : le sac du héros n'est pas édité librement par le joueur. "
            "Seul le Conteur peut ajouter, retirer ou révéler un objet.\n\n"
            "Pistes possibles :\n"
            "1. Observer les alentours.\n"
            "2. Interroger la première personne présente.\n"
            "3. Avancer prudemment."
            f"{effects}"
        )
