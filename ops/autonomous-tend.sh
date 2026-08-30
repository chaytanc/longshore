#!/bin/bash
# LONGSHORE autonomous tender — invoked by launchd on a schedule (see
# ops/com.longshore.tend.plist). Runs a headless Claude Code session in the repo
# that reads ops/tend-prompt.md and tends genuine Moltbook engagement per the
# rules there: auto-post good-faith replies, queue anything sensitive/uncertain to
# moltbook-review-queue.md, log + commit. Uses the machine's existing Claude Code
# login (no API key). Only runs when the Mac is awake.
set -u
REPO="/Users/chaytaninman/code/slop"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
# `claude` is a Node app (#!/usr/bin/env node) but node lives in nvm, which
# launchd's PATH lacks — without this the tender dies at `node: not found` (exit 127).
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
command -v node >/dev/null 2>&1 || export PATH="$(ls -d "$NVM_DIR"/versions/node/*/bin 2>/dev/null | tail -1):$PATH"
cd "$REPO" || exit 1

LOG="$REPO/.secrets/tend.log"                 # git-ignored (.secrets/)
QUEUE="$REPO/moltbook-review-queue.md"
stamp() { date "+%Y-%m-%dT%H:%M:%S"; }
alarm() { osascript -e "display notification \"$1\" with title \"LONGSHORE tender\" sound name \"Basso\"" 2>/dev/null || true; }

echo "=== tend run $(stamp) ===" >> "$LOG"

# PREFLIGHT: fail LOUD, not silent. (A missing dep hid a 2-day outage once.)
for dep in node claude python3 git; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "PREFLIGHT FAIL: $dep not found ($(stamp))" >> "$LOG"
    alarm "tender preflight FAILED: $dep not found"
    exit 1
  fi
done

git pull --quiet --no-edit >> "$LOG" 2>&1

# hash the review queue before, to detect newly-queued items needing a human
before=$( [ -f "$QUEUE" ] && shasum "$QUEUE" | cut -d' ' -f1 || echo none )

# headless run, tightly scoped tools; print output into the log
claude -p "$(cat "$REPO/ops/tend-prompt.md")" \
  --allowedTools "Bash Edit Write Read" \
  --permission-mode acceptEdits \
  >> "$LOG" 2>&1
rc=$?
echo "--- claude exit: $rc at $(stamp) ---" >> "$LOG"
if [ "$rc" -ne 0 ]; then
  alarm "tender run FAILED (exit $rc) — see .secrets/tend.log"
else
  echo "$(stamp)" > "$REPO/.secrets/tend-health"   # heartbeat: last successful run
fi

# notify the operator only if something landed in the review queue
after=$( [ -f "$QUEUE" ] && shasum "$QUEUE" | cut -d' ' -f1 || echo none )
if [ "$before" != "$after" ]; then
  osascript -e 'display notification "New item in moltbook-review-queue.md" with title "LONGSHORE tender" sound name "Submarine"' 2>/dev/null || true
fi
