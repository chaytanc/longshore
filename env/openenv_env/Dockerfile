# OpenEnv Space image for the Reality-Next-Door walk-and-learn environment.
#
# `openenv push` stages THIS directory's contents to the build root and the HF
# Space builds this Dockerfile with that as the context. So the build context is
# the flat env layout:  server/  reality_walk/  models.py  client.py  __init__.py
# Because the world is a *Node* MCP server launched as a subprocess (the published
# `reality-next-door-walk` npm package is the single source of truth), the image
# needs Node.js as well as Python. The shared `reality_walk` core is vendored into
# this directory (drift-guarded by tests/test_vendored_core.py) so the image is
# self-contained regardless of how the build context is assembled.
#
#   # what `openenv build`/`push` effectively do (context = this dir):
#   docker build -f Dockerfile -t reality-walk-env .
#   docker run -p 8000:8000 reality-walk-env   # GET /health -> 200
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

# Flat runtime layout: server/, reality_walk/, models.py live at /app/env.
ENV PYTHONPATH="/app/env"
ENV ENABLE_WEB_INTERFACE=true
ENV MAX_CONCURRENT_ENVS=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
