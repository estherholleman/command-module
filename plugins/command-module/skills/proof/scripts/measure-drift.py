#!/usr/bin/env python3
"""Measure writing-defect density in a repo's committed prose over time.

Why this exists: the writing-style references are maintained by hand, and the
2026-08-27 refresh established that new defect families arrive faster than
anyone notices them by reading. Three families were only found because they were
measured, not read. This script re-runs those measurements so drift shows up as
a number instead of an irritation.

What it measures: added lines only, from `git log -p` filtered to lines starting
with `+`, bucketed by period, normalised per 1,000 added words. Deletions are
ignored, so these are flow approximations rather than a census of the corpus.
Tables, code blocks and front matter are counted in the denominator. That is
deliberate: it matches the method used for the 2026-08-27 baseline, and
comparability against that baseline matters more than a purer denominator.

Usage:
    measure-drift.py                          # default repo, last 6 fortnights, vs baseline
    measure-drift.py --repo ~/prog/foo        # a different repo
    measure-drift.py --path docs/articles     # a narrower subtree
    measure-drift.py --periods 10             # more history
    measure-drift.py --no-baseline            # just the table

Exit status is 0 always; this reports, it does not gate.
"""

import argparse
import datetime as dt
import os
import re
import subprocess
import sys

DEFAULT_REPO = os.path.expanduser("~/prog/portfoliostrategyframework")
DEFAULT_PATH = "docs"

# Baseline measured 2026-08-27 over portfoliostrategyframework/docs by THIS script,
# so a re-run compares like with like. "pre" is 2026-05-01 to 2026-07-13, the stable
# window before the em dash rule was hardened; "aug" is 2026-08-14 to 2026-08-28, the
# worst observed fortnight. Reproduce with:
#   measure-drift.py --no-baseline --window 2026-05-01:2026-07-13 --window 2026-08-14:2026-08-28
#
# These differ from the ad-hoc figures quoted in the 2026-08-27 research document,
# which used narrower windows and slightly different expressions. The direction and
# rough magnitude agree; the exact numbers do not, and these are the ones to compare
# a re-run against because the same instrument produced them.
BASELINE = {
    "em_dash":      {"pre": 19.09, "aug": 9.58,  "note": "fell when the rule hardened on 07-13, then held"},
    "colon":        {"pre": 20.56, "aug": 18.88, "note": "context; this counts labels and headings too"},
    "semicolon":    {"pre": 14.42, "aug": 15.17, "note": "context; the ban applies to sentence glue only"},
    "tail_narrow":  {"pre": 0.019, "aug": 0.334, "note": "the two anchor forms only"},
    "tail_general": {"pre": 0.057, "aug": 0.731, "note": "the real shape; 13x rise"},
    "tail_en":      {"pre": 0.033, "aug": 0.017, "note": "English, thin sample, no trend"},
    "coord_indep":  {"pre": 0.286, "aug": 1.637, "note": "comma + en + a new independent clause; 6x"},
    "comma_en":     {"pre": 0.969, "aug": 4.956, "note": "all comma + en joins; 5x"},
    "subord":       {"pre": 0.607, "aug": 1.390, "note": "only doubled while coordination rose 5x"},
    "frag_proxy":   {"pre": 0.135, "aug": 0.164, "note": "verbless connector fragments; weak signal"},
    "_ratio":       {"pre": 1.60,  "aug": 3.56,  "note": "coordination to subordination"},
}

# Each metric is (label, regex, language, "lower is better" or "context").
METRICS = [
    ("em_dash", re.compile("\u2014"), "both", "lower"),
    ("colon", re.compile(r"\S:\s"), "both", "lower"),
    ("semicolon", re.compile(r";"), "both", "lower"),
    # NL 2.9 as originally written: only the two anchor verb forms.
    ("tail_narrow", re.compile(
        r",\s*(?:en|maar)\s+(?:daar|dat|hier|dit)\s+(?:zit|is|ligt|wringt|schuilt|weegt|knelt)\b",
        re.I), "nl", "lower"),
    # NL 2.9 as it now stands: the shape, with any predicate.
    ("tail_general", re.compile(
        r",\s*(?:en|maar)\s+(?:die|dat|daar|hier|deze|dit|ze|het)\s+"
        r"(?:hoort|horen|is|zijn|was|waren|maakt|maken|doet|doen|werkt|werken|geldt|gelden|"
        r"past|passen|hangt|hangen|valt|vallen|komt|komen|staat|staan|versterkt|versterken|"
        r"vult|vullen|betekent|betekenen|volgt|volgen|verschilt|verschillen|zit|ligt|wringt|"
        r"schuilt|weegt|knelt|blijkt|blijken|telt|tellen)\b", re.I), "nl", "lower"),
    # EN 2.9 equivalent.
    ("tail_en", re.compile(
        r",\s*(?:and|but)?\s*(?:that'?s|which is|therein lies|there lies|and that)\s+"
        r"(?:the|exactly|precisely|why|what)\b", re.I), "en", "lower"),
    # NL 2.11 / EN 2.10: comma + en followed by a new independent clause.
    ("coord_indep", re.compile(
        r",\s+en\s+(?:de|het|een|die|dat|deze|zijn|haar|hun|[A-Z])\w*\s+\w+(?:t|te|de|den|en)\b",
        re.I), "nl", "lower"),
    # The coordination ratio was established on Dutch prose. Both halves stay
    # Dutch-only so the number means the same thing on a re-run; mixing English
    # "and"/"because" into a Dutch corpus shifts it without anything changing.
    ("comma_en", re.compile(r",\s+en\s+"), "nl", "context"),
    ("subord", re.compile(
        r"\b(?:waardoor|omdat|zodat|terwijl|hoewel|doordat|aangezien)\b",
        re.I), "nl", "context"),
    # NL 2.8: verbless connector fragments.
    ("frag_proxy", re.compile(
        r",\s*(?:wat|consistent met|in lijn met|conform|which|consistent with)\s[^.!?\n]{0,60}\.",
        re.I), "both", "lower"),
]


def fortnights(n, end=None):
    """Return n consecutive fortnight windows ending today, oldest first."""
    end = end or dt.date.today()
    out = []
    for i in range(n, 0, -1):
        b = end - dt.timedelta(days=14 * (i - 1))
        a = end - dt.timedelta(days=14 * i)
        out.append((a.isoformat(), b.isoformat()))
    return out


def added_words(repo, path, since, until):
    """Concatenate every line added to `path` in the window."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", f"--since={since}", f"--until={until}",
             "-p", "--format=", "--", path],
            capture_output=True, text=True, errors="replace", check=False).stdout
    except FileNotFoundError:
        sys.exit("git not found on PATH")
    return "\n".join(l[1:] for l in out.split("\n")
                     if l.startswith("+") and not l.startswith("+++"))


def measure(text):
    words = len(text.split()) or 1
    row = {"words": words}
    for name, rx, _lang, _dir in METRICS:
        row[name] = len(rx.findall(text)) / words * 1000
    row["ratio"] = row["comma_en"] / row["subord"] if row["subord"] else float("nan")
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--path", default=DEFAULT_PATH)
    ap.add_argument("--periods", type=int, default=6, help="how many fortnights back")
    ap.add_argument("--no-baseline", action="store_true")
    ap.add_argument("--window", action="append", metavar="SINCE:UNTIL",
                    help="explicit window, repeatable; overrides --periods")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(args.repo, ".git")):
        sys.exit(f"not a git repo: {args.repo}")

    print(f"repo   {args.repo}")
    print(f"path   {args.path}")
    print("units  occurrences per 1,000 added words, added lines only\n")

    cols = ["em_dash", "colon", "semicolon", "tail_narrow", "tail_general",
            "tail_en", "coord_indep", "comma_en", "subord", "frag_proxy"]
    head = f"{'window':<24}{'words':>8}" + "".join(f"{c[:9]:>10}" for c in cols) + f"{'c:s':>7}"
    print(head)
    print("-" * len(head))

    windows = ([tuple(w.split(":", 1)) for w in args.window] if args.window
               else fortnights(args.periods))
    rows = []
    for since, until in windows:
        r = measure(added_words(args.repo, args.path, since, until))
        if r["words"] < 500:
            print(f"{since}..{until[5:]:<12}{r['words']:>8}   (too little added text to measure)")
            continue
        rows.append(((since, until), r))
        line = f"{since}..{until[5:]:<12}{r['words']:>8}"
        line += "".join(f"{r[c]:>10.3f}" if r[c] < 10 else f"{r[c]:>10.2f}" for c in cols)
        line += f"{r['ratio']:>7.2f}" if r["ratio"] == r["ratio"] else f"{'-':>7}"
        print(line)

    if args.no_baseline or not rows:
        return

    latest_window, latest = rows[-1]
    if latest_window[0] <= "2026-08-28" and latest_window[1] >= "2026-08-14":
        print("\nNote: the newest window overlaps the baseline window itself, so every")
        print("verdict below will read as unchanged. That is the expected state until")
        print("at least a fortnight of prose has been written under the new rules.")
    if latest["words"] < 5000:
        print("\nLatest window has under 5,000 added words. Too thin to read as a trend.")
        return

    print("\nAgainst the 2026-08-27 baseline (pre = stable May to mid-July, aug = worst fortnight)\n")
    print(f"{'metric':<15}{'pre':>9}{'aug':>9}{'now':>9}{'verdict':>12}   note")
    print("-" * 100)
    for name in ["em_dash", "colon", "semicolon", "tail_narrow", "tail_general",
                 "coord_indep", "comma_en", "subord", "frag_proxy"]:
        b = BASELINE.get(name)
        if not b:
            continue
        now, pre, aug = latest[name], b["pre"], b["aug"]
        # Every metric here is "lower is better", so the good end is whichever of
        # pre/aug is lower. Deriving it rather than assuming aug is the bad one:
        # the semicolon and em dash bans made aug the good state, and assuming
        # otherwise reported a regression as a recovery.
        good, bad = min(pre, aug), max(pre, aug)
        span = bad - good
        if span < 1e-9:
            verdict = "flat baseline"
        else:
            pos = (now - good) / span
            if pos <= 0.34:
                verdict = "holding" if good == aug else "recovered"
            elif pos <= 0.75:
                verdict = "improving" if good == aug else "partly back"
            elif pos <= 1.1:
                verdict = "unchanged"
            else:
                verdict = "worse"
        print(f"{name:<15}{pre:>9.3f}{aug:>9.3f}{now:>9.3f}{verdict:>12}   {b['note']}")

    r = BASELINE["_ratio"]
    print("\nThe single number to watch is the coordination-to-subordination ratio (c:s).")
    print(f"It sat at {r['pre']} in the stable window and reached {r['aug']} in the worst")
    print(f"fortnight. Falling back toward {r['pre']} means the always-on rules are reaching")
    print("generation. Sitting near {0} means they are not, which is the argument for".format(r["aug"]))
    print("adding the PostToolUse detector hook as a second layer.")
    if latest["ratio"] == latest["ratio"]:
        print(f"\nCurrent c:s ratio: {latest['ratio']:.2f}")


if __name__ == "__main__":
    main()
