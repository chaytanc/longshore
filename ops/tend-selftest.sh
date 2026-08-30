#!/bin/bash
# Tender self-test — reproduces launchd's STRIPPED runtime environment (the thing
# that hid the node-not-found break for two days) and verifies every dependency the
# tender needs. Run after ANY change to the wrapper, the plist, or the toolchain:
#     bash ops/tend-selftest.sh
# The key move: reset PATH to the launchd-minimal set FIRST, then apply the wrapper's
# own env logic — so a dep that only resolves in an interactive shell fails HERE,
# loudly, instead of silently in production.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"   # launchd-like; NOT the user shell PATH
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
command -v node >/dev/null 2>&1 || export PATH="$(ls -d "$NVM_DIR"/versions/node/*/bin 2>/dev/null | tail -1):$PATH"
cd "$(dirname "$0")/.." || { echo "FAIL: cannot cd to repo"; exit 1; }

fail=0
echo "== tender self-test (launchd-env simulation) =="
for c in node claude python3 git; do
  if command -v "$c" >/dev/null 2>&1; then echo "  ok: $c -> $(command -v "$c")"; else echo "  FAIL: '$c' not found on PATH"; fail=1; fi
done
claude --version >/dev/null 2>&1 && echo "  ok: claude runs (node resolves)" || { echo "  FAIL: 'claude --version' errored"; fail=1; }
python3 -c "import ops.moltbook as m" 2>/dev/null && echo "  ok: ops.moltbook imports" || { echo "  FAIL: ops.moltbook import"; fail=1; }
python3 -c "import ops.moltbook as m; d,_=m.api('/home'); exit(0 if d and d.get('your_account') else 1)" 2>/dev/null \
  && echo "  ok: Moltbook API reachable + key valid" || { echo "  FAIL: Moltbook API/key (need MOLTBOOK_API_KEY env or .secrets/moltbook)"; fail=1; }
git ls-remote --exit-code origin HEAD >/dev/null 2>&1 && echo "  ok: git remote reachable" || echo "  WARN: git remote unreachable (may be transient)"

if [ "$fail" -eq 0 ]; then echo "SELFTEST PASS — tender should run cleanly under launchd"; else echo "SELFTEST FAIL — fix before trusting the tender"; fi
exit "$fail"
