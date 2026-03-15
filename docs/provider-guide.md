# Adding a new provider

This guide shows how to create a new MCP tool provider using this project
as a template. Example: adding a **Wikipedia** provider.

## 1. Copy the project

```bash
cp -r mcp_server_brave mcp_server_wikipedia
cd mcp_server_wikipedia
```

## 2. Rename the package

Update `pyproject.toml`:

```toml
[project]
name = "mcp-server-wikipedia"

[project.scripts]
mcp-wikipedia = "mcp_server.cli.main:cli"
```

Update `settings.py` env prefix:

```python
model_config = SettingsConfigDict(env_prefix="MCP_WIKIPEDIA_", ...)
```

## 3. Create the provider

```
src/mcp_server/providers/wikipedia/
├── __init__.py
├── provider.py    # WikipediaProvider(ToolProvider)
├── client.py      # WikipediaClient — HTTP wrapper
└── schemas.py     # Optional response models
```

### provider.py

```python
from mcp_server.providers.base import ToolProvider
from mcp.types import Tool

class WikipediaProvider(ToolProvider):
    @property
    def provider_name(self) -> str:
        return "wikipedia"

    def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="search",
                description="Search Wikipedia articles.",
                inputSchema={...},
            ),
            Tool(
                name="get_article",
                description="Get the full text of a Wikipedia article.",
                inputSchema={...},
            ),
        ]

    async def call_tool(self, name: str, arguments: dict) -> str:
        if name == "search":
            return await self._client.search(arguments["query"])
        if name == "get_article":
            return await self._client.get_article(arguments["title"])
        raise ValueError(f"Unknown tool: {name}")
```

## 4. Wire it up

In `mcp/transport.py`, replace the Brave provider import:

```python
from mcp_server.providers.wikipedia.provider import WikipediaProvider

def mount_mcp_transport(app: FastAPI) -> None:
    provider = WikipediaProvider()
    register_provider(provider)
    # ... rest unchanged
```

## 5. Update settings

Add provider-specific settings (API keys, base URLs, etc.) to `settings.py`.

## 6. Update CLI

- Update server name in `mcp/server.py`: `Server("wikipedia")`
- Update health response in `monitoring/views.py`: `"provider": "wikipedia"`
- Update title in `web/application.py`

## 7. Test and run

```bash
uv sync
mcp-wikipedia doctor
mcp-wikipedia run
```

## Architecture reference

```
Transport (FastAPI + MCP SDK)
    ↓
MCP Protocol (server.py — list_tools / call_tool dispatch)
    ↓
Provider (your ToolProvider subclass)
    ↓
Client (HTTP wrapper for the external API)
```

Each layer is independent. The protocol and transport layers
are generic. Only the provider layer changes between servers.
