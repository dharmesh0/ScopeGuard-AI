import httpx

from app.core.config import get_settings
from app.services.search.base import SearchProvider, SearchResult


class TavilySearchProvider(SearchProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        if not self.settings.tavily_api_key:
            return []
        response = httpx.post(
            "https://api.tavily.com/search",
            json={"api_key": self.settings.tavily_api_key, "query": query, "max_results": limit},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return [
            SearchResult(title=item["title"], url=item["url"], snippet=item.get("content", ""))
            for item in data.get("results", [])
        ]

