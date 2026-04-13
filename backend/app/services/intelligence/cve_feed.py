from datetime import UTC, datetime, timedelta

import httpx

from app.services.search.factory import get_search_provider


class CVEFeedService:
    def latest(self, limit: int = 5) -> list[dict]:
        end = datetime.now(UTC)
        start = end - timedelta(days=14)
        response = httpx.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={
                "pubStartDate": start.isoformat().replace("+00:00", "Z"),
                "pubEndDate": end.isoformat().replace("+00:00", "Z"),
                "resultsPerPage": limit,
            },
            timeout=30,
        )
        response.raise_for_status()
        items = []
        for vuln in response.json().get("vulnerabilities", []):
            cve = vuln.get("cve", {})
            descriptions = cve.get("descriptions", [])
            description = descriptions[0].get("value", "") if descriptions else ""
            items.append(
                {
                    "id": cve.get("id"),
                    "description": description,
                    "source": "NVD",
                    "references": [ref.get("url") for ref in cve.get("references", [])[:3]],
                }
            )
        return items

    def safe_summary(self, query: str) -> list[dict]:
        search_results = get_search_provider().search(query, limit=3)
        return [{"title": item.title, "url": item.url, "snippet": item.snippet} for item in search_results]
