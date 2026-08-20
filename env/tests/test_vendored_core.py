# SPDX-License-Identifier: MIT
"""Drift guard: the vendored core in openenv_env/reality_walk/ MUST stay a
byte-for-byte copy of the canonical shared core in reality_walk/.

The copy exists only so `openenv push` (which packages just the openenv_env/
directory) produces a self-contained image. This test fails loudly if the two
ever diverge, so there is still effectively one source of truth.

Run:  ./.venv/bin/python tests/test_vendored_core.py   (or: pytest tests/)
"""

import sys
from pathlib import Path

ENV_DIR = Path(__file__).resolve().parent.parent
CANONICAL = ENV_DIR / "reality_walk"
VENDORED = ENV_DIR / "openenv_env" / "reality_walk"
CORE_FILES = ["__init__.py", "bridge.py", "task.py"]

_FAILURES = []


def check(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        _FAILURES.append(label)


def test_vendored_core_matches_canonical():
    for name in CORE_FILES:
        canonical = CANONICAL / name
        vendored = VENDORED / name
        check(f"vendored openenv_env/reality_walk/{name} exists", vendored.exists())
        if canonical.exists() and vendored.exists():
            same = canonical.read_bytes() == vendored.read_bytes()
            check(
                f"{name} is byte-identical to canonical reality_walk/{name}",
                same,
                "" if same else "DRIFT — re-copy reality_walk/ into openenv_env/",
            )


if __name__ == "__main__":
    test_vendored_core_matches_canonical()
    if _FAILURES:
        print(f"\n{len(_FAILURES)} check(s) failed: {_FAILURES}")
        sys.exit(1)
    print("\nVendored core is in sync.")
