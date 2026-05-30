#!/usr/bin/env python3
"""
youtube_comments.py -- extract YouTube comments (verbatim + deep links) via agent-browser.

Encodes the recipe the first live run worked out the hard way, so future runs don't
re-discover it:
  - comments are lazy-loaded: you MUST scrollIntoView('#comments') to hydrate them
    (a blind big scroll overshoots the trigger and yields ZERO comments);
  - the real per-comment permalink is the timestamp <a href="...&lc=ID">, NOT
    #published-time-text (that's a <span> with an empty href);
  - `agent-browser eval` returns its value JSON-ENCODED-AS-A-STRING, so it must be
    json.loads()'d up to twice.

Output: a JSON array on stdout, one object per comment:
  {"author","text","likes","lc","permalink","url"}
The DOM text IS the raw page, so each comment is already byte-true -- pipe it
straight into the database (the extracted text is its own raw source):
  ... | python verify_and_append_quote.py --raw - --quote "<text>" ...

Pick PROBLEM-TOPIC videos (regrets / cost / "should you really") -- glossy tour
videos yield generic praise and ~zero pain/WTP signal.

Usage:
  python youtube_comments.py --url "https://www.youtube.com/watch?v=VIDEOID" \
    [--scrolls 8] [--wait-ms 1500] [--auto-connect] [--keep-open]

Requires the `agent-browser` CLI on PATH. Stdlib only.
"""
import argparse
import json
import re
import subprocess
import sys

# JS run after hydration: collect one record per comment thread.
EXTRACT_JS = r"""
(() => {
  const out = [];
  document.querySelectorAll('ytd-comment-thread-renderer').forEach(t => {
    const text = (t.querySelector('#content-text')?.innerText || '').trim();
    if (!text) return;
    const author = (t.querySelector('#author-text')?.innerText || '').trim();
    const likes = (t.querySelector('#vote-count-middle')?.innerText || '').trim();
    let lc = '';
    const a = t.querySelector('a[href*="lc="]');
    if (a) { const m = a.href.match(/[?&]lc=([^&]+)/); if (m) lc = m[1]; }
    out.push({author, text, likes, lc});
  });
  return JSON.stringify(out);
})()
"""

SCROLL_INTO_VIEW_JS = (
    "var c=document.querySelector('#comments');"
    "c&&c.scrollIntoView({block:'start'});'ok'"
)


def video_id(url):
    m = re.search(r"[?&]v=([^&]+)", url) or re.search(r"youtu\.be/([^?&/]+)", url)
    if not m:
        sys.exit("Could not parse a video id from --url")
    return m.group(1)


def main():
    ap = argparse.ArgumentParser(description="Extract YouTube comments via agent-browser.")
    ap.add_argument("--url", required=True)
    ap.add_argument("--scrolls", type=int, default=8, help="Scroll-and-wait cycles (default 8).")
    ap.add_argument("--wait-ms", type=int, default=1500, help="Wait between scrolls (ms).")
    ap.add_argument("--auto-connect", action="store_true",
                    help="Drive the user's logged-in Chrome (helps with consent/region walls).")
    ap.add_argument("--keep-open", action="store_true", help="Don't close the browser at the end.")
    args = ap.parse_args()

    vid = video_id(args.url)
    base = ["agent-browser"] + (["--auto-connect"] if args.auto_connect else [])

    def ab(*a, stdin=None):
        r = subprocess.run(base + list(a), input=stdin, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(f"agent-browser {' '.join(a)} failed:\n{r.stderr}\n")
        return r.stdout

    # Navigate + hydrate the comment section.
    ab("open", args.url)
    ab("wait", "--load", "networkidle")
    ab("eval", "--stdin", stdin=SCROLL_INTO_VIEW_JS)
    ab("wait", "3500")
    for _ in range(max(0, args.scrolls)):
        ab("scroll", "down", "1300")
        ab("wait", str(args.wait_ms))

    raw_out = ab("eval", "--stdin", stdin=EXTRACT_JS)

    # agent-browser eval returns the value JSON-encoded-as-a-string: decode up to twice.
    data = None
    s = raw_out.strip()
    for _ in range(2):
        try:
            s = json.loads(s)
        except (ValueError, TypeError):
            break
        if not isinstance(s, str):
            data = s
            break
    if data is None:
        sys.stderr.write("Could not decode comment payload. Raw eval output was:\n"
                         + raw_out[:500] + "\n")
        return 1

    for c in data:
        c["permalink"] = (f"https://www.youtube.com/watch?v={vid}&lc={c['lc']}"
                          if c.get("lc") else "")
        c["url"] = c["permalink"] or args.url

    if not args.keep_open:
        ab("close")

    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    sys.stderr.write(f"\nExtracted {len(data)} comments from {vid}.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
