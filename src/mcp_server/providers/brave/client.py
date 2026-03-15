"""HTTP client for the Brave Search API."""

from __future__ import annotations

import asyncio

import httpx
from loguru import logger

from mcp_server.settings import settings


class BraveSearchClient:
    """Async wrapper around the Brave Search REST API with rate limiting."""

    def __init__(self) -> None:
        self._semaphore = asyncio.Semaphore(1)
        self._last_call: float = 0.0

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": settings.api_key,
        }

    async def _rate_limit(self) -> None:
        """Simple token-bucket: at most ``rate_limit_rps`` requests/sec."""
        async with self._semaphore:
            now = asyncio.get_event_loop().time()
            interval = 1.0 / settings.rate_limit_rps
            wait = self._last_call + interval - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = asyncio.get_event_loop().time()

    async def _get(self, path: str, params: dict) -> dict:
        """Make a rate-limited GET request to the Brave API."""
        await self._rate_limit()
        url = f"{settings.base_url}{path}"

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout, connect=5.0),
        ) as client:
            resp = await client.get(url, headers=self._headers(), params=params)

        if resp.status_code == 401:
            raise RuntimeError("Invalid Brave API key. Check MCP_BRAVE_API_KEY.")
        if resp.status_code == 429:
            raise RuntimeError("Brave API rate limit exceeded. Try again later.")
        if resp.status_code >= 500:
            raise RuntimeError(f"Brave API error (HTTP {resp.status_code}).")

        resp.raise_for_status()
        return resp.json()

    # ── Public methods ───────────────────────────────────────────

    async def web_search(
        self,
        query: str,
        count: int = 10,
        country: str = "",
        freshness: str = "",
    ) -> str:
        """Perform a web search and return markdown-formatted results."""
        params: dict[str, str | int] = {"q": query, "count": min(count, 20)}
        if country:
            params["country"] = country
        if freshness:
            params["freshness"] = freshness

        data = await self._get("/web/search", params)
        return self._format_web_results(data, query)

    async def local_search(self, query: str, count: int = 5) -> str:
        """Perform a local/places search and return formatted results."""
        params: dict[str, str | int] = {
            "q": query,
            "count": min(count, 5),
            "result_filter": "places",
        }
        data = await self._get("/web/search", params)
        return self._format_local_results(data, query)

    # ── Formatting ───────────────────────────────────────────────

    @staticmethod
    def _format_web_results(data: dict, query: str) -> str:
        results = data.get("web", {}).get("results", [])
        if not results:
            return f"No web results found for: {query}"

        lines = [f"## Web results for: {query}\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            snippet = r.get("description", "")
            lines.append(f"### {i}. {title}")
            lines.append(f"**URL:** {url}")
            if snippet:
                lines.append(f"{snippet}")
            lines.append("")

        # Include infobox if present
        infobox = data.get("infobox", {})
        if infobox and infobox.get("results"):
            info = infobox["results"][0]
            lines.append(f"---\n**Infobox:** {info.get('title', '')}")
            if info.get("description"):
                lines.append(info["description"])
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_local_results(data: dict, query: str) -> str:
        places = data.get("places", {}).get("results", [])
        if not places:
            return f"No local results found for: {query}"

        lines = [f"## Local results for: {query}\n"]
        for i, p in enumerate(places, 1):
            name = p.get("title", "Unknown")
            address = p.get("address", "")
            phone = p.get("phone", "")
            rating = p.get("rating", "")
            lines.append(f"### {i}. {name}")
            if address:
                lines.append(f"**Address:** {address}")
            if phone:
                lines.append(f"**Phone:** {phone}")
            if rating:
                lines.append(f"**Rating:** {rating}")
            lines.append("")

        return "\n".join(lines)
