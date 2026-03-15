"""Brave client response formatting tests."""

from __future__ import annotations

from mcp_server.providers.brave.client import BraveSearchClient


def test_format_web_results_with_data() -> None:
    data = {
        "web": {
            "results": [
                {
                    "title": "Example",
                    "url": "https://example.com",
                    "description": "An example page.",
                },
            ],
        },
    }
    result = BraveSearchClient._format_web_results(data, "test query")
    assert "Example" in result
    assert "https://example.com" in result
    assert "An example page." in result


def test_format_web_results_empty() -> None:
    result = BraveSearchClient._format_web_results({"web": {"results": []}}, "nothing")
    assert "No web results" in result


def test_format_local_results_with_data() -> None:
    data = {
        "places": {
            "results": [
                {
                    "title": "Joe's Pizza",
                    "address": "123 Main St",
                    "phone": "+1-555-1234",
                    "rating": "4.5",
                },
            ],
        },
    }
    result = BraveSearchClient._format_local_results(data, "pizza")
    assert "Joe's Pizza" in result
    assert "123 Main St" in result


def test_format_local_results_empty() -> None:
    result = BraveSearchClient._format_local_results({"places": {"results": []}}, "nothing")
    assert "No local results" in result
