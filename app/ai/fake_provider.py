from __future__ import annotations

from app.ai.base_provider import AIProvider


class FakeProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        return (
            "Le conteur de test se penche sur la scène.\n\n"
            "Votre action est prise en compte. Le monde réagit encore simplement pour l'instant, "
            "mais la boucle essentielle fonctionne : action, narration, mémoire.\n\n"
            "Pistes possibles :\n"
            "1. Observer les alentours.\n"
            "2. Interroger la première personne présente.\n"
            "3. Avancer prudemment."
        )
