import httpx

from app.core.config import get_settings
from app.services.search.base import SearchProvider, SearchResult


class SearxngSearchProvider(SearchProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        if not self.settings.searxng_base_url:
            return []
        response = httpx.get(
            f"{self.settings.searxng_base_url.rstrip('/')}/search",
            params={"q": query, "format": "json"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return [
            SearchResult(title=item["title"], url=item["url"], snippet=item.get("content", ""))
            for item in data.get("results", [])[:limit]
        ]

