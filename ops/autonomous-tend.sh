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

# headless run, tightly scoped tools; retry transient failures (claude -p has been
# exiting 1 with empty output — transient inference/API errors; a retry clears most).
rc=1
for attempt in 1 2 3; do
  echo "--- claude attempt $attempt at $(stamp) ---" >> "$LOG"
  PROMPT_OUT=$(claude -p "$(cat "$REPO/ops/tend-prompt.md")" \
    --allowedTools "Bash Edit Write Read" \
    --permission-mode acceptEdits 2>&1)
  rc=$?
  printf '%s\n' "$PROMPT_OUT" >> "$LOG"
  # success = exit 0 AND some output (empty output on exit 0 is also a soft failure)
  if [ "$rc" -eq 0 ] && [ -n "$PROMPT_OUT" ]; then break; fi
  echo "--- attempt $attempt rc=$rc, output ${#PROMPT_OUT} chars; backing off ---" >> "$LOG"
  sleep $((attempt * 30))
done
echo "--- claude exit: $rc at $(stamp) (after $attempt attempt(s)) ---" >> "$LOG"
if [ "$rc" -ne 0 ] || [ -z "$PROMPT_OUT" ]; then
  # VISIBLE failure record (committed, not just an unseen notification)
  echo "$(stamp) FAILED (exit $rc, ${#PROMPT_OUT} chars out) after $attempt attempts" > "$REPO/.secrets/tend-health"
  alarm "tender FAILED after retries (exit $rc) — see .secrets/tend.log"
  git config user.name 'autonomous-tend'; git config user.email 'longshore@users.noreply.github.com'
  echo "- $(stamp): tender run FAILED (exit $rc, empty/short output) after $attempt attempts — investigate" >> "$REPO/.secrets/tend-failures.log"
else
  echo "$(stamp) OK" > "$REPO/.secrets/tend-health"   # heartbeat: last successful run
fi

# notify the operator only if something landed in the review queue
after=$( [ -f "$QUEUE" ] && shasum "$QUEUE" | cut -d' ' -f1 || echo none )
if [ "$before" != "$after" ]; then
  osascript -e 'display notification "New item in moltbook-review-queue.md" with title "LONGSHORE tender" sound name "Submarine"' 2>/dev/null || true
fi
