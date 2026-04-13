from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        raise NotImplementedError

