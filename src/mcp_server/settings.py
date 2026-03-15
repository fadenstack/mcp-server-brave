"""Application settings — split into infrastructure (static) and provider (dynamic).

Infrastructure settings are loaded once at startup via environment variables
and are not changeable at runtime.

Provider settings can be updated at runtime through the settings REST API
and are persisted to disk.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp_server.services.settings_manager import SettingsManager


# ── Infrastructure settings (static, env-only) ──────────────────


class InfraSettings(BaseSettings):
    """Fixed infrastructure config — set via env vars, read-only at runtime."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_BRAVE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8100
    workers_count: int = 1
    reload: bool = False
    environment: str = "production"
    log_level: str = "info"
    auth_token: str = ""
    sentry_dsn: str = ""
    sentry_sample_rate: float = 1.0
    opentelemetry_endpoint: str = ""

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_token)


# ── Provider settings (dynamic, runtime-mutable) ────────────────


class BraveProviderSettings(BaseModel):
    """Brave Search provider config — mutable at runtime via REST API."""

    api_key: str = Field(
        default="",
        title="API Key",
        description="Brave Search API subscription token",
        json_schema_extra={"x-sensitive": True},
    )
    base_url: str = Field(
        default="https://api.search.brave.com/res/v1",
        title="Base URL",
        description="Brave Search API base URL",
    )
    rate_limit_rps: float = Field(
        default=1.0,
        title="Rate Limit (req/s)",
        description="Maximum requests per second to the Brave API",
        gt=0,
        le=100,
    )
    request_timeout: int = Field(
        default=15,
        title="Request Timeout",
        description="HTTP request timeout in seconds",
        ge=1,
        le=120,
    )


# ── Singletons ──────────────────────────────────────────────────

settings = InfraSettings()

provider_settings_manager: SettingsManager[BraveProviderSettings] = SettingsManager(
    schema_class=BraveProviderSettings,
    env_prefix="MCP_BRAVE_",
    persist_path="data/settings.json",
)
