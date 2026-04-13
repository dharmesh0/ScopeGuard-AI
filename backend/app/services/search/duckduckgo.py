import httpx

from app.services.search.base import SearchProvider, SearchResult


class DuckDuckGoSearchProvider(SearchProvider):
    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        response = httpx.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"}, timeout=20)
        response.raise_for_status()
        data = response.json()
        related = data.get("RelatedTopics", [])
        results: list[SearchResult] = []
        for item in related:
            if "Text" not in item or "FirstURL" not in item:
                continue
            results.append(SearchResult(title=item["Text"][:80], url=item["FirstURL"], snippet=item["Text"]))
            if len(results) >= limit:
                break
        return results

