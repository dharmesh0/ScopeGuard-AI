import httpx

from app.core.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.fallback_provider import FallbackProvider


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = FallbackProvider()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": self.settings.anthropic_model,
                "system": system_prompt,
                "max_tokens": 800,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        return "".join(block["text"] for block in payload["content"] if block["type"] == "text")

    def embed(self, text: str) -> list[float]:
        return self.fallback.embed(text)

