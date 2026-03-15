"""Brave Search provider — exposes web_search and local_search tools."""

from __future__ import annotations

from mcp.types import Tool

from mcp_server.providers.base import ToolProvider
from mcp_server.providers.brave.client import BraveSearchClient

_WEB_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query.",
        },
        "count": {
            "type": "integer",
            "description": "Number of results to return (1-20).",
            "default": 10,
        },
        "country": {
            "type": "string",
            "description": "Country code for results (e.g. US, DE). Empty for global.",
            "default": "",
        },
        "freshness": {
            "type": "string",
            "enum": ["", "pd", "pw", "pm", "py"],
            "description": "Freshness filter: pd=past day, pw=past week, pm=past month, py=past year.",
            "default": "",
        },
    },
    "required": ["query"],
}

_LOCAL_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Local search query (e.g. 'pizza near Berlin').",
        },
        "count": {
            "type": "integer",
            "description": "Number of results (1-5).",
            "default": 5,
        },
    },
    "required": ["query"],
}


class BraveSearchProvider(ToolProvider):
    """Brave Search as an MCP tool provider."""

    def __init__(self) -> None:
        self._client = BraveSearchClient()

    @property
    def provider_name(self) -> str:
        return "brave"

    def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="web_search",
                description=(
                    "Search the web using Brave Search. "
                    "Returns organic results with titles, URLs, and snippets."
                ),
                inputSchema=_WEB_SEARCH_SCHEMA,
            ),
            Tool(
                name="local_search",
                description=(
                    "Search for local businesses and places using Brave Local Search."
                ),
                inputSchema=_LOCAL_SEARCH_SCHEMA,
            ),
        ]

    async def call_tool(self, name: str, arguments: dict) -> str:
        if name == "web_search":
            return await self._client.web_search(
                query=arguments["query"],
                count=arguments.get("count", 10),
                country=arguments.get("country", ""),
                freshness=arguments.get("freshness", ""),
            )
        if name == "local_search":
            return await self._client.local_search(
                query=arguments["query"],
                count=arguments.get("count", 5),
            )
        raise ValueError(f"Unknown tool: {name}")
