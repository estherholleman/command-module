#!/usr/bin/env python3
"""
verify_and_append_quote.py -- self-verifying writer for the audience quotes database.

Appends ONE quote row to a quotes.jsonl store ONLY IF the quote text is provably
present in the raw source page. This makes `verbatim_verified` mechanical rather
than trust-based: the script, not the model, certifies the quote.

Verification strategy:
  1. Exact substring match against the raw page text (fast path).
  2. Fallback: a length-tolerant NORMALIZED match (curly -> straight quotes,
     en/em dashes -> hyphen, non-breaking / zero-width spaces, collapsed runs of
     whitespace) that maps back to the BYTE-EXACT slice of the raw page. That exact
     slice -- not the (possibly punctuation-drifted) input -- is what gets stored,
     so the saved quote always equals the page.

If neither matches, the row is rejected (exit 2) unless --allow-unverified, in
which case it is written with verbatim_verified=false and a note.

Usage:
  python verify_and_append_quote.py \
    --db docs/strategy/research/audiences/quotes.jsonl \
    --raw raw_page.txt \                 # or:  --raw -   to read raw text from stdin
    --segment tiny-house --bucket pain \
    --quote "their words (punctuation may differ slightly from the page)" \
    --platform blog-post --url "https://example.com/post#comment-12" \
    [--speaker "u/handle"] [--community "Adventuring with Shannon"] \
    [--date 2024-03-11] [--context "responding to ..."] \
    [--tags weight,storage] [--notes "single sentence, not stitched"] \
    [--captured 2026-05-30] [--allow-unverified] [--check]

  --check   Verify only; print the matched slice and exit (don't append).

Exit: 0 = verified (and appended unless --check); 2 = NOT verified. Stdlib only.
"""
import argparse
import datetime
import json
import sys

BUCKETS = {"pain", "want", "current_solution", "willingness_to_pay", "vocabulary", "other"}

# Length-preserving single-char substitutions (1 char -> 1 char), applied during
# normalization. Whitespace runs are collapsed separately (see _norm_map).
_CHAR = {
    "‘": "'", "’": "'", "‛": "'",          # curly single quotes
    "“": '"', "”": '"',                          # curly double quotes
    "–": "-", "—": "-", "‒": "-", "―": "-",  # dashes
    " ": " ", " ": " ", " ": " ",           # nbsp / thin / narrow nbsp
    "​": "",  "﻿": "",                            # zero-width chars (dropped)
}


def _norm_map(s):
    """Normalize for matching; return (norm_str, idx_map).

    idx_map[i] = index in the ORIGINAL string of the i-th normalized char, so a
    span found in norm_str can be mapped back to a byte-exact slice of `s`.
    Whitespace runs collapse to a single ' ' mapped to the first ws char's index.
    """
    out, idx = [], []
    prev_ws = False
    for i, ch in enumerate(s):
        c = _CHAR.get(ch, ch)
        if c == "":
            continue  # zero-width: drop entirely
        if c.isspace():
            if prev_ws:
                continue  # collapse run
            c = " "
            prev_ws = True
        else:
            prev_ws = False
        out.append(c)
        idx.append(i)
    return "".join(out), idx


def find_exact_slice(raw, query):
    """Return the byte-exact slice of `raw` that matches `query`, or None."""
    q = query.strip()
    if not q:
        return None
    # Fast path: exact substring.
    pos = raw.find(q)
    if pos >= 0:
        return raw[pos:pos + len(q)]
    # Normalized match -> map back to exact raw slice.
    nraw, rmap = _norm_map(raw)
    nq, _ = _norm_map(q)
    nq = nq.strip()
    if not nq:
        return None
    pos = nraw.find(nq)
    if pos < 0:
        return None
    start = rmap[pos]
    end = rmap[pos + len(nq) - 1] + 1
    return raw[start:end]


def main():
    ap = argparse.ArgumentParser(description="Self-verifying quotes.jsonl writer.")
    ap.add_argument("--db", required=True, help="Path to quotes.jsonl (created/appended).")
    ap.add_argument("--raw", required=True, help="Path to raw source text, or '-' for stdin.")
    ap.add_argument("--segment", required=True)
    ap.add_argument("--bucket", required=True, choices=sorted(BUCKETS))
    ap.add_argument("--quote", required=True)
    ap.add_argument("--platform", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--speaker", default="anon")
    ap.add_argument("--community", default="")
    ap.add_argument("--date", default=None, help="Post date YYYY-MM-DD (default null).")
    ap.add_argument("--context", default="")
    ap.add_argument("--tags", default="", help="Comma-separated.")
    ap.add_argument("--notes", default="")
    ap.add_argument("--captured", default=None, help="Run date YYYY-MM-DD (default today).")
    ap.add_argument("--allow-unverified", action="store_true",
                    help="Write with verbatim_verified=false instead of rejecting.")
    ap.add_argument("--check", action="store_true", help="Verify only; do not append.")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.raw == "-" else open(args.raw, encoding="utf-8").read()

    slice_ = find_exact_slice(raw, args.quote)
    verified = slice_ is not None

    if not verified and not args.allow_unverified:
        sys.stderr.write(
            "REJECTED: quote not found in raw source (exact or normalized).\n"
            "  Fix the quote to match the page, or pass --allow-unverified to "
            "store it as verbatim_verified=false.\n")
        return 2

    stored_quote = slice_ if verified else args.quote
    notes = args.notes
    if not verified:
        notes = ("UNVERIFIED: substring not found in raw source. " + notes).strip()

    if args.check:
        if verified:
            print("VERIFIED. Byte-exact slice that will be stored:\n" + stored_quote)
            return 0
        print("NOT VERIFIED: quote not present in raw source.", file=sys.stderr)
        return 2

    captured = args.captured or datetime.date.today().isoformat()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    row = {
        "segment": args.segment,
        "bucket": args.bucket,
        "quote": stored_quote,
        "verbatim_verified": verified,
        "speaker": args.speaker,
        "platform": args.platform,
        "community": args.community,
        "url": args.url,
        "date": args.date,
        "context": args.context,
        "captured": captured,
        "tags": tags,
        "notes": notes,
    }
    with open(args.db, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    status = "verbatim_verified=true" if verified else "verbatim_verified=FALSE"
    print(f"Appended ({status}) to {args.db}: {stored_quote[:70]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
