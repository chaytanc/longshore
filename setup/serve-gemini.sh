#!/usr/bin/env bash
# Serve the Gemini capsule locally so you can browse the REAL thing (gemini://), not just the HTML preview.
# Read before running. It installs a small Python Gemini server (jetforce) for your user and serves ./gemini.
# It exposes nothing beyond localhost. Ctrl-C to stop.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
say()  { printf "\n\033[36m▸ %s\033[0m\n" "$1"; }
warn() { printf "\n\033[33m! %s\033[0m\n" "$1"; }

if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 not found. Install Python 3 and re-run."; exit 1
fi

say "Installing jetforce (a small Python Gemini server), if needed"
python3 -m pip install --user --quiet jetforce || {
  warn "pip install failed. Try:  python3 -m pip install jetforce"; exit 1; }

# jetforce's console script installs to the user bin; find it whether or not that's on PATH.
JF="$(command -v jetforce || echo "$(python3 -m site --user-base)/bin/jetforce")"
if [ ! -x "$JF" ]; then
  warn "Couldn't locate the 'jetforce' command. It installed to your Python user bin —"
  warn "add that to PATH, or run:  python3 -m jetforce --dir ./gemini --hostname localhost"
  exit 1
fi

say "Serving ./gemini at gemini://localhost (Ctrl-C to stop)"
cat <<'EOF'
  To view it, install a Gemini client — Lagrange (GUI) is the easiest:
      macOS:   brew install --cask lagrange
      (or use a terminal client: amfora, bombadillo)
  then open:   gemini://localhost

  jetforce generates a self-signed TLS cert on first run; your client will ask you to
  trust it (that's normal for Gemini — "trust on first use").

  To host it PUBLICLY later (only when you launch): put ./gemini on any Gemini host —
  a small VPS running jetforce/agate/gmnisrv, or a managed capsule host (e.g. flounder.online,
  sourcehut pages with a gemini target). Point the door's links at that hostname.
EOF
echo
exec "$JF" --dir ./gemini --hostname localhost
