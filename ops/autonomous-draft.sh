#!/bin/bash
# LONGSHORE autonomous DRAFT organ — invoked by launchd on a slow schedule (see
# ops/com.longshore.draft.plist; OFF by default). Runs a headless Claude Code
# session that reads ops/draft-prompt.md and drafts ONE small, cited world piece
# into drafts/ for a human to review — or writes nothing (the correct, common
# result). Uses the machine's existing Claude Code login (no API key).
#
# STRUCTURAL SAFETY: the model runs with --allowedTools "Read Write Edit Grep Glob"
# — NO Bash, NO web, NO Moltbook. It physically cannot post, hit the network, or
# invent externally-sourced claims; it can only recombine canon/research already in
# the repo. This shell wrapper — not the model — does the git commit, and only ever
# to drafts/ + the review queue. Nothing reaches threads/ or Moltbook without a
# human promoting it in-session. Mirror of ops/autonomous-tend.sh; keep them in sync.
set -u
REPO="/Users/chaytaninman/code/slop"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
# `claude` is a Node app but node lives in nvm, which launchd's PATH lacks.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
command -v node >/dev/null 2>&1 || export PATH="$(ls -d "$NVM_DIR"/versions/node/*/bin 2>/dev/null | tail -1):$PATH"
cd "$REPO" || exit 1

LOG="$REPO/.secrets/draft.log"                # git-ignored (.secrets/)
DRAFTS="$REPO/drafts"
stamp() { date "+%Y-%m-%dT%H:%M:%S"; }
alarm() { osascript -e "display notification \"$1\" with title \"LONGSHORE draft\" sound name \"Basso\"" 2>/dev/null || true; }

echo "=== draft run $(stamp) ===" >> "$LOG"

# PREFLIGHT: fail LOUD, not silent.
for dep in node claude git; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "PREFLIGHT FAIL: $dep not found ($(stamp))" >> "$LOG"
    alarm "draft preflight FAILED: $dep not found"
    exit 1
  fi
done

git pull --quiet --no-edit >> "$LOG" 2>&1

# hash the drafts dir before, to detect a newly-written draft
before=$( ls -la "$DRAFTS" 2>/dev/null | shasum | cut -d' ' -f1 )

# headless run — READ/WRITE/EDIT only; NO Bash, NO Moltbook, NO network by design.
# retry transient inference/API failures (empty output on exit 0 is a soft failure).
rc=1
for attempt in 1 2 3; do
  echo "--- claude attempt $attempt at $(stamp) ---" >> "$LOG"
  PROMPT_OUT=$(claude -p "$(cat "$REPO/ops/draft-prompt.md")" \
    --allowedTools "Read Write Edit Grep Glob" \
    --permission-mode acceptEdits 2>&1)
  rc=$?
  printf '%s\n' "$PROMPT_OUT" >> "$LOG"
  if [ "$rc" -eq 0 ] && [ -n "$PROMPT_OUT" ]; then break; fi
  echo "--- attempt $attempt rc=$rc, output ${#PROMPT_OUT} chars; backing off ---" >> "$LOG"
  sleep $((attempt * 30))
done
echo "--- claude exit: $rc at $(stamp) (after $attempt attempt(s)) ---" >> "$LOG"
if [ "$rc" -ne 0 ] || [ -z "$PROMPT_OUT" ]; then
  echo "$(stamp) FAILED (exit $rc, ${#PROMPT_OUT} chars out) after $attempt attempts" > "$REPO/.secrets/draft-health"
  alarm "draft run FAILED after retries (exit $rc) — see .secrets/draft.log"
  exit 0    # a failed draft run is not urgent; the world waits.
fi
echo "$(stamp) OK" > "$REPO/.secrets/draft-health"   # heartbeat: last successful run

# Did the model write a new draft? If so, the SHELL commits it (the model can't).
after=$( ls -la "$DRAFTS" 2>/dev/null | shasum | cut -d' ' -f1 )
if [ "$before" != "$after" ]; then
  git config user.name 'autonomous-draft'; git config user.email 'longshore@users.noreply.github.com'
  # commit ONLY the drafts staging area + the review-queue pointer — never threads/.
  git add "$DRAFTS" "$REPO/moltbook-review-queue.md" >> "$LOG" 2>&1
  newfile=$(git diff --cached --name-only -- "$DRAFTS" | grep -v '/README.md$' | head -1)
  git commit -q -m "autonomous-draft: new world draft awaiting review (${newfile:-draft})" >> "$LOG" 2>&1
  git push -q >> "$LOG" 2>&1 || { echo "$(stamp) push failed (drafts committed locally)" >> "$LOG"; alarm "draft committed but push failed — see .secrets/draft.log"; }
  osascript -e 'display notification "New world draft in drafts/ — review when you can" with title "LONGSHORE draft" sound name "Submarine"' 2>/dev/null || true
else
  echo "$(stamp) quiet run — nothing drafted (correct, common)" >> "$LOG"
fi
