from app.core.config import get_settings
from app.services.search.base import SearchProvider
from app.services.search.duckduckgo import DuckDuckGoSearchProvider
from app.services.search.searxng import SearxngSearchProvider
from app.services.search.tavily import TavilySearchProvider


def get_search_provider() -> SearchProvider:
    provider = get_settings().search_provider.lower()
    if provider == "searxng":
        return SearxngSearchProvider()
    if provider == "tavily":
        return TavilySearchProvider()
    return DuckDuckGoSearchProvider()

