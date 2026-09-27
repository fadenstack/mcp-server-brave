ARG BASE_IMAGE=faden/base:latest
FROM ${BASE_IMAGE} AS prod

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --inexact --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --inexact --no-dev

EXPOSE 8100

CMD ["/usr/local/bin/python", "-m", "mcp_server"]

# ── Dev target ───────────────────────────────────────────────────
FROM prod AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-groups
