from __future__ import annotations

from app.ai.base_provider import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.model = model or "gpt-4.1-mini"

    def generate(self, prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Le package openai n'est pas installé. Lance : pip install openai") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(model=self.model, input=prompt)
        return response.output_text
