# MCP Server — Brave Search

Standalone [Model Context Protocol](https://modelcontextprotocol.io/) server that
exposes **Brave Search** as MCP tools for [Fadenstack](https://github.com/fadenstack).

## Tools provided

| Tool           | Description                                                       |
| -------------- | ----------------------------------------------------------------- |
| `web_search`   | Full web search with result count, country, and freshness filters |
| `local_search` | Local business/places search                                      |

## Quick start

```bash
# Clone and install
git clone https://github.com/fadenstack/mcp-server-brave.git
cd mcp-server-brave
uv sync

# Configure
cp .env.example .env
# Edit .env — set MCP_BRAVE_API_KEY

# Validate
mcp-brave doctor

# Run
mcp-brave run
```

The server starts at `http://localhost:8100` with the MCP endpoint at `/mcp`.

## Docker

```bash
# Build and run
mcp-brave docker-up --build

# Or directly
docker compose up -d --build
```

## Register with Fadenstack

The server speaks **Streamable HTTP**. In the Fadenstack console, open **Extensions → MCP Hub** and choose
**Register Server**:

| Field       | Value                                          |
| ----------- | ---------------------------------------------- |
| Name        | Brave Search                                   |
| Transport   | Streamable HTTP                                |
| URL         | `http://mcp-brave:8100/mcp`                    |
| Tool Prefix | `brave`                                        |
| Headers     | `Authorization: Bearer <MCP_BRAVE_AUTH_TOKEN>` |

Or through the API, as an administrator (a login token from `POST /api/auth/jwt/login`):

```bash
curl -X POST https://<your-fadenstack-server>/api/admin/mcp/servers \
  -H "Authorization: Bearer <admin-login-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brave Search",
    "transport": "streamable_http",
    "url": "http://mcp-brave:8100/mcp",
    "tool_prefix": "brave",
    "headers": {"Authorization": "Bearer <MCP_BRAVE_AUTH_TOKEN>"},
    "auto_discover": true,
    "enabled": true
  }'
```

## CLI commands

| Command                 | Purpose                          |
| ----------------------- | -------------------------------- |
| `mcp-brave run`         | Start the server                 |
| `mcp-brave doctor`      | Validate config and test API key |
| `mcp-brave manifest`    | Print tool manifest as JSON      |
| `mcp-brave docker-up`   | Start via Docker Compose         |
| `mcp-brave docker-down` | Stop Docker container            |

## Configuration

All settings via environment variables (prefix `MCP_BRAVE_`):

| Variable                    | Default      | Description                                                            |
| --------------------------- | ------------ | ---------------------------------------------------------------------- |
| `MCP_BRAVE_API_KEY`         | _(required)_ | Brave Search API key                                                   |
| `MCP_BRAVE_HOST`            | `0.0.0.0`    | Bind host                                                              |
| `MCP_BRAVE_PORT`            | `8100`       | Bind port                                                              |
| `MCP_BRAVE_AUTH_TOKEN`      | _(empty)_    | If set, incoming requests must include `Authorization: Bearer <token>` |
| `MCP_BRAVE_RATE_LIMIT_RPS`  | `1`          | Max requests per second to Brave API                                   |
| `MCP_BRAVE_REQUEST_TIMEOUT` | `15`         | HTTP timeout (seconds) for Brave API calls                             |
| `MCP_BRAVE_LOG_LEVEL`       | `info`       | Logging level                                                          |

## Creating new providers

See [docs/provider-guide.md](docs/provider-guide.md) for how to add a new
provider using this project as a template.

## License

Apache-2.0
