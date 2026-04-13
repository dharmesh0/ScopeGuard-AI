import hashlib
from collections import Counter

from app.services.llm.base import LLMProvider


class FallbackProvider(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        del system_prompt
        lines = [line.strip() for line in user_prompt.splitlines() if line.strip()]
        severity_words = Counter(word.lower().strip(".,:") for word in " ".join(lines).split())
        highlights = []
        for keyword in ("critical", "high", "medium", "expired", "missing"):
            if severity_words[keyword]:
                highlights.append(f"{keyword} signals: {severity_words[keyword]}")
        if not highlights:
            highlights.append("No high-confidence severe conditions were inferred from the current evidence.")
        return "Fallback analysis summary:\n" + "\n".join(f"- {line}" for line in highlights[:5])

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        while len(values) < 64:
            for byte in digest:
                values.append((byte / 255.0) * 2 - 1)
                if len(values) == 64:
                    break
            digest = hashlib.sha256(digest).digest()
        return values

