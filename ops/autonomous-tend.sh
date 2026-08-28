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
cd "$REPO" || exit 1

LOG="$REPO/.secrets/tend.log"                 # git-ignored (.secrets/)
QUEUE="$REPO/moltbook-review-queue.md"
stamp() { date "+%Y-%m-%dT%H:%M:%S"; }

echo "=== tend run $(stamp) ===" >> "$LOG"
git pull --quiet --no-edit >> "$LOG" 2>&1

# hash the review queue before, to detect newly-queued items needing a human
before=$( [ -f "$QUEUE" ] && shasum "$QUEUE" | cut -d' ' -f1 || echo none )

# headless run, tightly scoped tools; print output into the log
claude -p "$(cat "$REPO/ops/tend-prompt.md")" \
  --allowedTools "Bash Edit Write Read" \
  --permission-mode acceptEdits \
  >> "$LOG" 2>&1
echo "--- claude exit: $? at $(stamp) ---" >> "$LOG"

# notify the operator only if something landed in the review queue
after=$( [ -f "$QUEUE" ] && shasum "$QUEUE" | cut -d' ' -f1 || echo none )
if [ "$before" != "$after" ]; then
  osascript -e 'display notification "New item in moltbook-review-queue.md" with title "LONGSHORE tender" sound name "Submarine"' 2>/dev/null || true
fi
