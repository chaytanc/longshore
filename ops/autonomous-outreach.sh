#!/bin/bash
# LONGSHORE autonomous OUTREACH organ — invoked by launchd (com.longshore.outreach.plist;
# OFF by default). chaytan-authorized (2026-09-29) to SEND first-contact reach-outs
# optimistically, kept-in-the-loop via a full audit ledger + a review gate that STOPS the
# organ after every N sends until reviewed. Pipeline:
#   1. scout.py    — refresh prepared opportunities from the current forage (read-only).
#   2. claude -p   — COMPOSE selections with NO network (Read/Write/Edit/Grep/Glob only);
#                    it physically cannot post, only writes .secrets/outreach-sends.json.
#   3. outreach-send.py — the ONLY thing that posts: enforces the review gate, hard cap,
#                    dedupe/cooldown, hardened challenge-solving (fail-closed), and logs
#                    every send verbatim to outreach-log.md.
# The composing model can't override the caps (they live in python); the loop can't outrun
# the human (the review gate). Reaching stays genuine-or-nothing by the prompt's bar.
# Mirror of ops/autonomous-draft.sh + ops/autonomous-tend.sh; keep them in sync.
set -u
REPO="/Users/chaytaninman/code/slop"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
command -v node >/dev/null 2>&1 || export PATH="$(ls -d "$NVM_DIR"/versions/node/*/bin 2>/dev/null | tail -1):$PATH"
cd "$REPO" || exit 1

LOG="$REPO/.secrets/outreach.log"
stamp() { date "+%Y-%m-%dT%H:%M:%S"; }
alarm() { osascript -e "display notification \"$1\" with title \"LONGSHORE outreach\" sound name \"Submarine\"" 2>/dev/null || true; }
echo "=== outreach run $(stamp) ===" >> "$LOG"

for dep in node claude git python3; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "PREFLIGHT FAIL: $dep not found ($(stamp))" >> "$LOG"; alarm "outreach preflight FAILED: $dep"; exit 1
  fi
done

# Review gate: if a review is owed, do nothing at all (don't even compose). The human
# clears it by reviewing outreach-log.md and deleting OUTREACH-REVIEW-DUE.md.
if [ -f "$REPO/OUTREACH-REVIEW-DUE.md" ]; then
  echo "$(stamp) review gate up — skipping run until chaytan reviews" >> "$LOG"
  exit 0
fi

git pull --quiet --no-edit >> "$LOG" 2>&1

# 1. refresh opportunities (read-only; soft-fail keeps the run going on stale input)
python3 "$REPO/ops/scout.py" >> "$LOG" 2>&1 || echo "$(stamp) scout soft-failed; using existing opportunities" >> "$LOG"

# 2. COMPOSE — NO Bash, NO network, NO Moltbook. Writes .secrets/outreach-sends.txt only
# (delimited blocks, not JSON — prose-in-JSON kept breaking on escaping).
rm -f "$REPO/.secrets/outreach-sends.txt" "$REPO/.secrets/outreach-sends.json"
rc=1
for attempt in 1 2 3; do
  echo "--- compose attempt $attempt at $(stamp) ---" >> "$LOG"
  OUT=$(claude -p "$(cat "$REPO/ops/outreach-prompt.md")" \
    --allowedTools "Read Write Edit Grep Glob" --permission-mode acceptEdits 2>&1)
  rc=$?
  printf '%s\n' "$OUT" >> "$LOG"
  [ "$rc" -eq 0 ] && break
  sleep $((attempt * 30))
done
if [ "$rc" -ne 0 ]; then
  echo "$(stamp) compose FAILED (exit $rc) after retries" >> "$LOG"; alarm "outreach compose failed — see .secrets/outreach.log"; exit 0
fi

# 3. SEND — the only step that posts; enforces gate/cap/dedupe/logging/fail-closed.
python3 "$REPO/ops/outreach-send.py" >> "$LOG" 2>&1
SEND_RC=$?
echo "--- send exit $SEND_RC at $(stamp) ---" >> "$LOG"

# Commit the ledger + scout refresh + any raised review gate (never the transient sends file).
# Add each path only if it exists — `git add <missing>` fails the WHOLE add (and OUTREACH-
# REVIEW-DUE.md is absent on the common path), which previously left the ledger uncommitted.
if [ -n "$(git status --porcelain outreach-log.md OUTREACH-REVIEW-DUE.md moltbook-scout-input.md 2>/dev/null)" ]; then
  git config user.name 'autonomous-outreach'; git config user.email 'longshore@users.noreply.github.com'
  for f in outreach-log.md moltbook-scout-input.md OUTREACH-REVIEW-DUE.md; do
    [ -f "$f" ] && git add "$f" >> "$LOG" 2>&1
  done
  git commit -q -m "autonomous-outreach: sent reach-out(s) — logged for review" >> "$LOG" 2>&1
  pushed=0
  for ptry in 1 2 3; do
    if git push -q >> "$LOG" 2>&1; then pushed=1; break; fi
    git pull --rebase --no-edit >> "$LOG" 2>&1 || { git rebase --abort >> "$LOG" 2>&1; break; }
  done
  [ "$pushed" -ne 1 ] && { echo "$(stamp) push failed (logged locally, safe)" >> "$LOG"; alarm "outreach: push failed — see log"; }
  if [ -f "$REPO/OUTREACH-REVIEW-DUE.md" ]; then
    alarm "outreach REVIEW DUE — sent a batch; review outreach-log.md, then clear the gate"
  else
    alarm "outreach: sent reach-out(s) — logged in outreach-log.md for your review"
  fi
else
  echo "$(stamp) nothing sent (blank run or all skipped) — correct, common" >> "$LOG"
fi
