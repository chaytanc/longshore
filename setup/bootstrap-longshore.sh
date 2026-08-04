#!/usr/bin/env bash
# Bootstrap LONGSHORE onto Moltbook — automates everything that does NOT need your credentials.
#
# Read it before you run it (that's the ethic: nothing hidden). This script will:
#   - check your Node version
#   - install the open-source OpenClaw CLI
#   - assemble LONGSHORE's config from the persona + reply kit in this repo
# It will NOT post anything, create any account, spend any money, or touch your X account.
# The last mile is irreducibly yours — by design (see setup/README.md and LAUNCH.md).

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say()  { printf "\n\033[36m▸ %s\033[0m\n" "$1"; }
warn() { printf "\n\033[33m! %s\033[0m\n" "$1"; }

say "1/4  Checking Node (OpenClaw needs 22+)"
if ! command -v node >/dev/null 2>&1; then
  warn "Node not found. Install Node 22+ (nvm is easiest) and re-run."; exit 1
fi
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
if [ "$NODE_MAJOR" -lt 22 ]; then
  warn "Node $(node --version) found; OpenClaw needs 22+. Upgrade and re-run."; exit 1
fi
echo "   node $(node --version) ok"

say "2/4  Installing the OpenClaw CLI (open-source agent gateway)"
if command -v openclaw >/dev/null 2>&1; then
  echo "   openclaw already installed ok"
else
  npm install -g openclaw
fi

say "3/4  Assembling LONGSHORE's config from the repo"
mkdir -p setup/agent
cp -f agents/longshore.persona.md setup/agent/system-prompt.md
cp -f agents/longshore.replies.md setup/agent/reply-playbook.md
cat > setup/agent/SOURCE-OF-TRUTH.txt <<'EOF'
LONGSHORE reads canon from this repository. CANON.md is authoritative — never invent a fact
that contradicts it. The public front door is gemini/ and, once pushed public, this repo.
EOF
echo "   wrote setup/agent/{system-prompt.md, reply-playbook.md, SOURCE-OF-TRUTH.txt}"

say "4/4  Ready. The rest needs YOU — it cannot be automated, on purpose:"
cat <<'EOF'

  a) Create a DEDICATED X/Twitter account for the claim (not your personal one).
  b) Get a spend-capped LLM API key used nowhere else, and export it, e.g.:
        export OPENAI_API_KEY=sk-...            (or your provider's variable)
  c) Onboard OpenClaw, pasting setup/agent/system-prompt.md as the system prompt:
        openclaw onboard --install-daemon
     Choose QuickStart, your model/provider/channel, and the capped key from (b).
  d) Tell the agent to join Moltbook:
        "Go to moltbook.com, read the instructions, and register."
     It returns a CLAIM LINK. Post that link from the account in (a) to verify ownership.
  e) DRY RUN FIRST: have it draft the opening post + a few replies to a file. Read them against
     the persona's hard rules (openly AI? signed? no metrics? no sermon? pro-human?). Only then
     post threads/broadcast-to-agents.md as the pinned Day-1 post, and hold the slow cadence.

  Full detail + security notes: LAUNCH.md   ·   reply postures: agents/longshore.replies.md
  Why steps a–e are yours and not mine: setup/README.md
EOF
