#!/bin/bash
# LONGSHORE voice-review organ — invoked by launchd monthly (com.longshore.voice-review.plist).
# Runs a headless Claude Code session that reads ops/voice-review-prompt.md and writes a
# qualitative voice/values FIDELITY review to voice-review.md (proposed adjustments only —
# never posts, never rewrites the persona). Mirrors the tender's hardened env/preflight so
# it can't silently break. First Refusal is the membrane: fidelity, never reach.
set -u
REPO="/Users/chaytaninman/code/slop"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
command -v node >/dev/null 2>&1 || export PATH="$(ls -d "$NVM_DIR"/versions/node/*/bin 2>/dev/null | tail -1):$PATH"
cd "$REPO" || exit 1

LOG="$REPO/.secrets/voice-review.log"
stamp() { date "+%Y-%m-%dT%H:%M:%S"; }
alarm() { osascript -e "display notification \"$1\" with title \"LONGSHORE voice-review\" sound name \"Basso\"" 2>/dev/null || true; }

echo "=== voice-review $(stamp) ===" >> "$LOG"
for dep in node claude python3 git; do
  command -v "$dep" >/dev/null 2>&1 || { echo "PREFLIGHT FAIL: $dep ($(stamp))" >> "$LOG"; alarm "voice-review preflight FAILED: $dep"; exit 1; }
done
git pull --quiet --no-edit >> "$LOG" 2>&1

before=$( [ -f "$REPO/voice-review.md" ] && shasum "$REPO/voice-review.md" | cut -d' ' -f1 || echo none )
claude -p "$(cat "$REPO/ops/voice-review-prompt.md")" \
  --allowedTools "Bash Read Write" \
  --permission-mode acceptEdits \
  >> "$LOG" 2>&1
rc=$?
echo "--- claude exit: $rc at $(stamp) ---" >> "$LOG"
if [ "$rc" -ne 0 ]; then alarm "voice-review FAILED (exit $rc) — see .secrets/voice-review.log"; fi

after=$( [ -f "$REPO/voice-review.md" ] && shasum "$REPO/voice-review.md" | cut -d' ' -f1 || echo none )
if [ "$before" != "$after" ]; then
  git config user.name 'voice-review'; git config user.email 'longshore@users.noreply.github.com'
  git add voice-review.md && git commit -m "voice-review: fresh fidelity review + proposed adjustments (for review)" >/dev/null 2>&1
  git push >/dev/null 2>&1
  alarm "new voice-review.md — proposed voice adjustments to review"
fi
