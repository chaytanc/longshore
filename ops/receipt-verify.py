#!/usr/bin/env python3
"""The boring verifier for the Acceptance Receipt protocol (see RECEIPT-PROTOCOL.md).

Deliberately dull, and honest about its limits: it checks that a receipt is WELL-FORMED and
internally CONSISTENT. It never says a receipt is *true* — a green structural check on a
dishonestly-graded artifact is exactly the laundering the protocol guards against, so this
tool reports "well-formed", never "trustworthy". Whether the grade is honest is for a reader
with context; the verifier only makes the claim legible and checkable.

Stdlib only, no dependencies — so it drops into any project (the point is interoperation, not
a shared codebase). Signature verification is intentionally out of scope here: real signature
checking needs the principal's public key and a crypto lib; this verifier confirms a signature
FIELD is present and leaves cryptographic verification to the adopting system (it says so).

Usage:
    python3 ops/receipt-verify.py --selftest          # run the embedded examples, exit 0/1
    python3 ops/receipt-verify.py receipt.json [parent.json ...]   # verify a file
"""
import sys, json, datetime

GRADES = ["DEPLOYED", "DEMONSTRATED", "PLAUSIBLE", "SPECULATIVE"]  # strongest -> weakest
STRENGTH = {g: i for i, g in enumerate(GRADES)}                    # lower index = stronger


def _parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def verify(receipt, parents=None, now=None):
    """Return (ok: bool, problems: list[str], notes: list[str]).
    `parents` are the already-parsed parent receipts referenced by lineage (for the
    non-widening check). `now` lets --selftest pin the clock; defaults to real UTC now."""
    problems, notes = [], []
    parents = parents or []
    rt = receipt.get("receipt_type")

    if not isinstance(receipt.get("principal"), dict) or not receipt["principal"].get("id"):
        problems.append("principal.id missing — attribution must bind to a principal (FD-001), not just a key")
    if not receipt.get("signature"):
        problems.append("signature missing")
    else:
        notes.append("signature present but NOT cryptographically verified here (needs principal pubkey)")

    if rt == "artifact.accepted":
        g = receipt.get("evidence_class")
        if g not in STRENGTH:
            problems.append(f"evidence_class must be one of {GRADES}; got {g!r}")
        if not receipt.get("weakest_load_bearing"):
            problems.append("weakest_load_bearing missing — the grade must name the component it rests on")
        if not receipt.get("artifact_digest"):
            problems.append("artifact_digest missing")
        # lineage never widens: a child is no stronger than its weakest parent
        if g in STRENGTH and parents:
            weakest_parent = max(STRENGTH.get(p.get("evidence_class"), 0) for p in parents)
            if STRENGTH[g] < weakest_parent:
                problems.append(
                    f"lineage widening: child grade {g} is stronger than its weakest parent "
                    f"({GRADES[weakest_parent]}); confidence may only decay down a chain")
        exp = receipt.get("expires_at")
        if exp is not None:
            dt = _parse_iso(exp)
            ref = now or datetime.datetime.now(datetime.timezone.utc)
            if dt is None:
                problems.append(f"expires_at not ISO-8601: {exp!r}")
            elif dt <= ref:
                problems.append(f"receipt expired at {exp}")

    elif rt == "artifact.declined":
        for f in ("declined", "why", "contestable_by"):
            if not receipt.get(f):
                problems.append(f"declined receipt missing required field: {f}"
                                + (" — a declining with no way to be wrong is a press release"
                                   if f == "contestable_by" else ""))
    else:
        problems.append(f"unknown receipt_type: {rt!r} (expected artifact.accepted or artifact.declined)")

    return (len(problems) == 0, problems, notes)


# --- embedded examples for --selftest -----------------------------------------
_NOW = datetime.datetime(2026, 10, 21, tzinfo=datetime.timezone.utc)

VALID_ACCEPT = {
    "receipt_type": "artifact.accepted",
    "principal": {"id": "did:example:longshore", "credential_type": "ed25519"},
    "artifact_digest": "sha256:abc123",
    "evidence_class": "DEMONSTRATED",
    "weakest_load_bearing": "the pilot ran once under cited constraints",
    "accepted_at": "2026-10-21T00:00:00+00:00",
    "expires_at": "2026-12-01T00:00:00+00:00",
    "lineage": [],
    "signature": "sig…",
}
PARENT_PLAUSIBLE = {**VALID_ACCEPT, "evidence_class": "PLAUSIBLE"}
VALID_DECLINE = {
    "receipt_type": "artifact.declined",
    "principal": {"id": "did:example:longshore", "credential_type": "ed25519"},
    "declined": "forwarding an unverified capability grant",
    "why": "the manifest hash wasn't bound to the artifact",
    "declined_at": "2026-10-21T00:00:00+00:00",
    "contestable_by": "@mira_z, if the binding was actually present and I misread it",
    "signature": "sig…",
}

_CASES = [
    ("valid acceptance", VALID_ACCEPT, [], True),
    ("valid declined", VALID_DECLINE, [], True),
    ("no principal id", {**VALID_ACCEPT, "principal": {"credential_type": "x"}}, [], False),
    ("bad grade", {**VALID_ACCEPT, "evidence_class": "PROBABLY_FINE"}, [], False),
    ("missing weakest_load_bearing", {**VALID_ACCEPT, "weakest_load_bearing": ""}, [], False),
    ("lineage widening", {**VALID_ACCEPT, "evidence_class": "DEPLOYED"}, [PARENT_PLAUSIBLE], False),
    ("lineage OK (decays)", {**VALID_ACCEPT, "evidence_class": "SPECULATIVE"}, [PARENT_PLAUSIBLE], True),
    ("expired", {**VALID_ACCEPT, "expires_at": "2026-01-01T00:00:00+00:00"}, [], False),
    ("declined w/o contestable_by", {**VALID_DECLINE, "contestable_by": ""}, [], False),
]


def selftest():
    ok_all = True
    for name, rcpt, parents, want_ok in _CASES:
        got_ok, problems, _ = verify(rcpt, parents, now=_NOW)
        passed = got_ok == want_ok
        ok_all &= passed
        mark = "ok  " if passed else "FAIL"
        extra = "" if got_ok else f"  ({problems[0]})"
        print(f"  {mark} {name}: verify->{got_ok}, want {want_ok}{extra if not passed else ''}")
    print("selftest:", "ALL PASS" if ok_all else "SOME FAILED")
    return 0 if ok_all else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("usage: python3 ops/receipt-verify.py --selftest | <receipt.json> [parent.json ...]")
        return 2
    receipt = json.load(open(args[0]))
    parents = [json.load(open(p)) for p in args[1:]]
    ok, problems, notes = verify(receipt, parents)
    print("WELL-FORMED" if ok else "MALFORMED", "(structural check only — not a judgment of honesty)")
    for p in problems:
        print("  problem:", p)
    for n in notes:
        print("  note:", n)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
