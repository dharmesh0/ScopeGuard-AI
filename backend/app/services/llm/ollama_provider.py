import httpx

from app.core.config import get_settings
from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/chat",
            json={
                "model": self.settings.ollama_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=45,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def embed(self, text: str) -> list[float]:
        response = httpx.post(
            f"{self.settings.ollama_base_url}/api/embeddings",
            json={"model": self.settings.ollama_model, "prompt": text},
            timeout=45,
        )
        response.raise_for_status()
        return response.json()["embedding"][:64]

