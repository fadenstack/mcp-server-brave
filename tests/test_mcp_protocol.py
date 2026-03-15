"""Test MCP tool definitions are valid."""

from __future__ import annotations

import pytest


def test_brave_provider_lists_tools() -> None:
    from mcp_server.providers.brave.provider import BraveSearchProvider

    provider = BraveSearchProvider()
    tools = provider.list_tools()

    assert len(tools) == 2
    names = {t.name for t in tools}
    assert "web_search" in names
    assert "local_search" in names

    for tool in tools:
        assert tool.description
        assert tool.inputSchema
        assert "query" in tool.inputSchema["properties"]
        assert "query" in tool.inputSchema["required"]


def test_brave_provider_name() -> None:
    from mcp_server.providers.brave.provider import BraveSearchProvider

    assert BraveSearchProvider().provider_name == "brave"
