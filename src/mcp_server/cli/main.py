"""Dedicated CLI for the Brave Search MCP server."""

from __future__ import annotations

import json
import subprocess
import sys

import click

from mcp_server.settings import settings


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.version_option(package_name="mcp-server-brave")
@click.pass_context
def cli(ctx: click.Context, *, verbose: bool) -> None:
    """mcp-brave — Standalone MCP server for Brave Search."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--host", default=None, help="Bind host (overrides MCP_BRAVE_HOST).")
@click.option("--port", default=None, type=int, help="Bind port (overrides MCP_BRAVE_PORT).")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development.")
def run(host: str | None, port: int | None, *, reload: bool) -> None:
    """Start the MCP server."""
    import uvicorn

    uvicorn.run(
        "mcp_server.web.application:get_app",
        host=host or settings.host,
        port=port or settings.port,
        workers=settings.workers_count,
        reload=reload or settings.reload,
        factory=True,
    )


@cli.command()
def doctor() -> None:
    """Validate configuration and test Brave API connectivity."""
    errors: list[str] = []
    warnings: list[str] = []

    click.echo("Checking configuration...\n")

    # API key
    if not settings.api_key:
        errors.append("MCP_BRAVE_API_KEY is not set.")
    else:
        click.echo("  [OK] API key configured")

    # Auth token
    if settings.auth_enabled:
        click.echo("  [OK] Auth token set (incoming requests will be validated)")
    else:
        warnings.append("No MCP_BRAVE_AUTH_TOKEN set — server accepts unauthenticated requests.")

    # Test API connectivity
    if settings.api_key:
        click.echo("\nTesting Brave API connectivity...")
        import httpx

        try:
            resp = httpx.get(
                f"{settings.base_url}/web/search",
                params={"q": "test", "count": 1},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": settings.api_key,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                click.echo("  [OK] Brave API reachable and key is valid")
            elif resp.status_code == 401:
                errors.append("Brave API key is invalid (HTTP 401).")
            elif resp.status_code == 429:
                warnings.append("Brave API rate-limited (HTTP 429) — key is valid but quota may be low.")
            else:
                errors.append(f"Brave API returned HTTP {resp.status_code}.")
        except httpx.ConnectError:
            errors.append("Cannot reach Brave API — check network/firewall.")
        except httpx.TimeoutException:
            errors.append("Brave API request timed out.")

    # Summary
    click.echo("")
    for w in warnings:
        click.echo(click.style(f"  [WARN] {w}", fg="yellow"))
    for e in errors:
        click.echo(click.style(f"  [FAIL] {e}", fg="red"))

    if errors:
        click.echo(click.style("\nDoctor found issues. Fix them before starting.", fg="red"))
        raise SystemExit(1)

    click.echo(click.style("\nAll checks passed.", fg="green"))


@cli.command()
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output.")
def manifest(*, pretty: bool) -> None:
    """Print the MCP tool manifest as JSON (for registration/debugging)."""
    from mcp_server.providers.brave.provider import BraveSearchProvider

    provider = BraveSearchProvider()
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "inputSchema": t.inputSchema,
        }
        for t in provider.list_tools()
    ]

    output = {
        "server_name": "brave-search",
        "provider": provider.provider_name,
        "transport": "streamable-http",
        "endpoint": f"http://{settings.host}:{settings.port}/mcp",
        "tools": tools,
    }
    indent = 2 if pretty else None
    click.echo(json.dumps(output, indent=indent))


@cli.command("docker-up")
@click.option("--build", is_flag=True, help="Rebuild the image before starting.")
@click.option("--dev", is_flag=True, help="Use dev compose overrides.")
def docker_up(*, build: bool, dev: bool) -> None:
    """Build and start the Docker container."""
    cmd = ["docker", "compose"]
    if dev:
        cmd.extend(["-f", "docker-compose.yml", "-f", "deploy/docker-compose.dev.yml"])
    cmd.append("up")
    if build:
        cmd.append("--build")
    cmd.append("-d")
    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


@cli.command("docker-down")
def docker_down() -> None:
    """Stop and remove the Docker container."""
    cmd = ["docker", "compose", "down"]
    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    cli()
