# The walkable world, containerized — supports Glama's introspection check and
# anyone who'd rather run it in a container. Self-contained: node + two deps,
# no build step, speaks MCP over stdio. Read-only; makes no network calls.
FROM node:20-slim
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY server.js ./
CMD ["node", "server.js"]
