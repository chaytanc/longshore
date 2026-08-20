# OpenEnv Space image for the Reality-Next-Door walk-and-learn environment.
#
# Unlike a typical OpenEnv env, this one launches a *Node* MCP server as a
# subprocess (the published `reality-next-door-walk` npm package is the world's
# single source of truth), so the image needs Node.js as well as Python. Build
# context is the env/ directory (so the shared `reality_walk` core is included).
#
#   docker build -f openenv_env/Dockerfile -t reality-walk-env .
#   docker run -p 8000:8000 reality-walk-env
#
# At runtime the server runs `npx -y reality-next-door-walk`, which fetches the
# package on first use (the only network access; the walk server itself makes
# none). For a fully offline image, COPY a vendored copy of walk/ in and set
# WALK_SERVER_JS to its server.js.

FROM python:3.12-slim

# Node.js (for the walk MCP server launched via npx).
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/env
COPY . /app/env

# Python deps: the bridge + OpenEnv adapter, plus the FastAPI server stack.
RUN pip install --no-cache-dir \
    "mcp==1.29.0" "openenv==0.4.1" \
    "fastapi>=0.115.0" "uvicorn>=0.24.0" "pydantic>=2.0.0"

ENV PYTHONPATH="/app/env:${PYTHONPATH}"
ENV ENABLE_WEB_INTERFACE=true
ENV MAX_CONCURRENT_ENVS=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "openenv_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
