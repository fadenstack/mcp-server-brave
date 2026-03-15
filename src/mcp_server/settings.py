"""Application settings — pydantic-settings with env var binding."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the Brave Search MCP server.

    All values can be overridden via environment variables prefixed
    with ``MCP_BRAVE_``.  A ``.env`` file in the working directory
    is loaded automatically.
    """

    model_config = SettingsConfigDict(
        env_prefix="MCP_BRAVE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Server ───────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8100
    workers_count: int = 1
    reload: bool = False
    environment: str = "production"
    log_level: str = "info"

    # ── Auth (optional) ──────────────────────────────────────────
    auth_token: str = ""

    # ── Brave Search API ─────────────────────────────────────────
    api_key: str = ""
    base_url: str = "https://api.search.brave.com/res/v1"
    rate_limit_rps: float = 1.0
    request_timeout: int = 15

    # ── Observability ────────────────────────────────────────────
    sentry_dsn: str = ""
    sentry_sample_rate: float = 1.0
    opentelemetry_endpoint: str = ""

    # ── Derived ──────────────────────────────────────────────────

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_token)


settings = Settings()
