#!/usr/bin/env python3
"""Standalone tests for the 2026-07-09 engagement + reconciliation changes.
Run: /usr/bin/python3 test_engagement.py   (no pytest; asserts + a tiny runner)."""
import importlib.util, json, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SHARED = Path(__file__).resolve().parents[2] / "staging" / "hooks" / "_clock_shared.py"
spec = importlib.util.spec_from_file_location("_clock_shared", SHARED)
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

T0 = datetime(2026, 7, 9, 9, 0, 0)
def at(mins): return T0 + timedelta(minutes=mins)
def armed():
    return {"session_id": "s", "repo": "r", "cluster": "c", "opened_at": S._fmt(T0),
            "start": None, "work_start": None, "last_activity": None, "accrued_seconds": 0,
            "tool_count": 0, "turn_count": 0, "first_turn_at": None, "wrapped_at": None}

results = []
def check(name, cond):
    results.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name)

# 1. Turn-based start backdates to first turn after threshold.
c = armed()
S.register_engagement(c, at(0), is_tool=False)
check("turn1: not started", not S.has_started(c) and c["turn_count"] == 1 and c["first_turn_at"] == S._fmt(at(0)))
S.register_engagement(c, at(5), is_tool=False)
check("turn2: started, backdated to turn1", S.has_started(c) and c["start"] == S._fmt(at(0)) and c["work_start"] == S._fmt(at(0)))
ws, end, mins = S.honest_span(c, now=at(5))
check("turn start span ~5min", mins == 5 and ws == at(0) and end == at(5))

# 2. A substantive tool starts immediately (no threshold wait).
c = armed()
S.register_engagement(c, at(0), is_tool=True)
check("tool: immediate start", S.has_started(c) and c["start"] == S._fmt(at(0)) and c["tool_count"] == 1)

# 3. Work -> idle(>30) -> work: idle excluded, pre-gap work preserved (accrual).
c = armed()
S.register_engagement(c, at(0), is_tool=True)     # start
S.register_engagement(c, at(10), is_tool=False)   # +10 (gap 10<30) advance
S.register_engagement(c, at(50), is_tool=False)   # gap 40>30 -> seal [0,10]=10min, restart at 50
check("accrued 10min after idle roll", c["accrued_seconds"] == 600 and c["start"] == S._fmt(at(50)))
S.register_engagement(c, at(55), is_tool=False)   # +5 in the new sub-span
ws, end, mins = S.honest_span(c, now=at(55))
check("work-idle-work bills 15 not 55", mins == 15 and ws == at(0) and end == at(55))

# 4. Never backdate a turn-start across an idle gap between the first two turns.
c = armed()
S.register_engagement(c, at(0), is_tool=False)    # first_turn_at=0
S.register_engagement(c, at(40), is_tool=False)   # gap 40>30 -> start at now, not backdated
check("no backdate across idle", c["start"] == S._fmt(at(40)))

# 5. reconcile_from_transcript: cluster + gap-split + since filter + UTC->local.
def utc(mins):
    # local wall time == at(mins); emit as UTC Z (subtract local offset)
    localdt = at(mins)
    off = localdt.astimezone().utcoffset()
    return (localdt - off).strftime("%Y-%m-%dT%H:%M:%S.000Z")
lines = []
for m in (0, 5, 12, 60, 63):   # cluster A: 0..12 (12min), gap, cluster B: 60..63 (3min) = 15min
    lines.append(json.dumps({"type": "user", "timestamp": utc(m), "isSidechain": False}))
lines.append(json.dumps({"type": "assistant", "timestamp": utc(2), "isSidechain": True}))  # ignored
lines.append(json.dumps({"type": "summary", "timestamp": utc(2)}))  # ignored (not user/assistant)
tf = Path(tempfile.mkdtemp()) / "t.jsonl"; tf.write_text("\n".join(lines) + "\n")
r = S.reconcile_from_transcript(str(tf), now=at(120))
check("reconcile 12+3=15min, 2 spans", r and r["minutes"] == 15 and r["spans"] == 2)
check("reconcile local first/last", r and r["first"] == at(0) and r["last"] == at(63))
r2 = S.reconcile_from_transcript(str(tf), since=at(30), now=at(120))
check("reconcile since-filter -> only cluster B (3min)", r2 and r2["minutes"] == 3 and r2["spans"] == 1)

# 6. finalize_row method selection.
# 6a clock only (no transcript)
c = armed(); S.register_engagement(c, at(0), is_tool=True); S.register_engagement(c, at(20), is_tool=False)
res = S.finalize_row(c, now=at(20))
check("finalize clock method", res and res[3] == "clock" and res[2] == 20)
# 6b transcript tail bigger -> reconciled
c = armed(); S.register_engagement(c, at(0), is_tool=True); S.register_engagement(c, at(5), is_tool=False)
c["transcript_path"] = str(tf)   # transcript says 15min > clock's 5min
res = S.finalize_row(c, now=at(120))
check("finalize reconciled when transcript bigger", res and res[3] == "reconciled" and res[2] == 15)
# 6c armed-only (never started) + transcript -> reconstructed
c = armed(); c["transcript_path"] = str(tf)
res = S.finalize_row(c, now=at(120))
check("finalize reconstructed for armed-only w/ transcript", res and res[3] == "reconstructed" and res[2] == 15)
# 6d armed-only, no transcript -> drain (None)
c = armed()
check("finalize drain armed-only no transcript", S.finalize_row(c, now=at(120)) is None)
# 6e legacy (no opened_at) -> drain even with transcript
c = armed(); del c["opened_at"]; c["start"] = S._fmt(at(0)); c["transcript_path"] = str(tf)
check("finalize drain legacy", S.finalize_row(c, now=at(120)) is None)

# 7. Idempotent-ish: honest_span None for armed, minutes floor.
check("honest_span None when not started", S.honest_span(armed()) is None)

fails = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (sum(1 for _, ok in results if ok), len(results)))
sys.exit(1 if fails else 0)
