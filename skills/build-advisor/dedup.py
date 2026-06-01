#!/usr/bin/env python3
"""
dedup.py — Quality & redundancy pass for an advisor corpus (stdlib only, no installs).

What it does (safe, deterministic):
  1. Strips common promo/boilerplate phrases (like/subscribe, sponsor reads, "link in bio").
  2. Detects NEAR-DUPLICATE SECTIONS (the same talk re-posted on YouTube + podcast, or a clip
     that's a subset of a longer video) via word-shingle Jaccard similarity. Keeps the longest
     instance, drops the rest.
  3. REPORTS repeated passages (the recurring origin-story / framework spiel said across many
     sources) — but does NOT auto-cut them, since slicing verbatim transcripts is risky. You
     decide whether to prune from the report.
  4. Prints a coverage + redundancy report (sections, words, by platform, dup clusters).

It expects the corpus format this plugin produces:
    ======================================================================
    ### <title>
    # author: <name> | platform: <YouTube|X|Podcast|...> | source: <url>
    ======================================================================

    <body text>

USAGE:
    python dedup.py corpus.txt                 # dry run — report only, writes nothing
    python dedup.py corpus.txt --apply         # writes corpus.cleaned.txt (original untouched)
    python dedup.py corpus.txt --apply --similarity 0.85   # tune dup threshold (default 0.80)

The original file is NEVER modified; --apply writes a new <name>.cleaned.txt next to it.
"""

import argparse
import re
import sys
from collections import Counter

BAR = "=" * 70

# Best-effort promo/boilerplate phrases to strip inline. Add your own.
PROMO_PATTERNS = [
    r"(?i)\b(?:so |and |now )?(?:make sure (?:to |you )?|don'?t forget to |be sure to )?"
    r"(?:smash|hit|tap|click)(?:ing)? (?:that |the )?(?:like|subscribe)(?: button)?"
    r"(?:[ ,and]+(?:subscribe|like|hit the bell|ring the bell|notification[s]?))*",
    r"(?i)\blink(?:s)? (?:in|down in) the (?:description|bio|comments)\b",
    r"(?i)\bsubscribe to (?:the|my|our) channel\b",
    r"(?i)\b(?:this (?:video|episode) is )?sponsored by [^.]{0,60}",
    r"(?i)\buse (?:code|coupon|promo code) [A-Za-z0-9]+\b",
    r"(?i)\b(?:check out|head (?:over )?to) (?:the )?(?:link|description)[^.]{0,40}",
    r"(?i)\bhit the bell( icon)?\b",
    r"(?i)\bturn on (?:post )?notifications\b",
]

SECTION_RE = re.compile(
    r"={70}\n### (?P<title>.*?)\n(?P<meta># .*?)\n={70}\n(?P<body>.*?)"
    r"(?=\n={70}\n### |\Z)",
    re.DOTALL,
)


def shingles(text, n=5):
    """Set of n-word shingles (lowercased) — a fingerprint for similarity comparison."""
    words = re.findall(r"\w+", text.lower())
    return {" ".join(words[i : i + n]) for i in range(max(0, len(words) - n + 1))}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def strip_promo(body):
    removed = 0
    for pat in PROMO_PATTERNS:
        body, n = re.subn(pat, " ", body)
        removed += n
    body = re.sub(r"[ \t]{2,}", " ", body).strip()
    return body, removed


def word_count(text):
    return len(re.findall(r"\w+", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", help="corpus .txt file in the plugin's section format")
    ap.add_argument("--apply", action="store_true", help="write <name>.cleaned.txt")
    ap.add_argument("--similarity", type=float, default=0.80,
                    help="section near-duplicate threshold (0-1, default 0.80)")
    args = ap.parse_args()

    raw = open(args.corpus, encoding="utf-8").read()
    preamble = raw[: raw.find(BAR)] if BAR in raw else ""
    sections = [m.groupdict() for m in SECTION_RE.finditer(raw)]
    if not sections:
        sys.exit("No sections found — is this a corpus file in the expected format?")

    # 1) strip promo boilerplate
    promo_removed = 0
    for s in sections:
        s["body"], n = strip_promo(s["body"])
        promo_removed += n
        s["shingles"] = shingles(s["body"])
        s["words"] = word_count(s["body"])

    # 2) near-duplicate sections → keep the longest, drop the rest
    dropped, clusters = set(), []
    for i in range(len(sections)):
        if i in dropped:
            continue
        group = [i]
        for j in range(i + 1, len(sections)):
            if j in dropped:
                continue
            if jaccard(sections[i]["shingles"], sections[j]["shingles"]) >= args.similarity:
                group.append(j)
        if len(group) > 1:
            keep = max(group, key=lambda k: sections[k]["words"])
            for k in group:
                if k != keep:
                    dropped.add(k)
            clusters.append((keep, [k for k in group if k != keep]))

    # 3) repeated-passage report (recurring spiels across sections) — report only
    big_shingles = Counter()
    for s in sections:
        for sh in shingles(s["body"], n=12):
            big_shingles[sh] += 1
    repeated = [(sh, c) for sh, c in big_shingles.most_common(15) if c >= 3]

    # ---- report ----
    plats = Counter(re.search(r"platform:\s*([^|]+)", s["meta"]).group(1).strip()
                    if re.search(r"platform:\s*([^|]+)", s["meta"]) else "?"
                    for s in sections)
    kept = [s for i, s in enumerate(sections) if i not in dropped]
    print("=" * 60)
    print("CORPUS QUALITY REPORT")
    print("=" * 60)
    print(f"Sections:            {len(sections)}  ({len(kept)} kept, {len(dropped)} near-dup dropped)")
    print(f"Words:               {sum(s['words'] for s in sections):,} -> "
          f"{sum(s['words'] for s in kept):,} after dedup")
    print(f"Promo phrases stripped: {promo_removed}")
    print(f"By platform:         {dict(plats)}")
    if clusters:
        print("\nNear-duplicate sections (kept the longest, dropped the rest):")
        for keep, drops in clusters:
            print(f"  KEEP: {sections[keep]['title'][:60]}")
            for d in drops:
                print(f"   drop: {sections[d]['title'][:60]}")
    else:
        print("\nNo near-duplicate sections found.")
    if repeated:
        print("\nFrequently repeated phrases (likely recurring spiels — review, prune if noise):")
        for sh, c in repeated[:8]:
            print(f"  x{c}: \"{sh[:70]}...\"")
    print("=" * 60)

    if args.apply:
        out_path = re.sub(r"\.txt$", "", args.corpus) + ".cleaned.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            if preamble.strip():
                f.write(preamble.rstrip() + "\n\n")
            for i, s in enumerate(sections):
                if i in dropped:
                    continue
                f.write(f"{BAR}\n### {s['title']}\n{s['meta']}\n{BAR}\n\n{s['body']}\n\n")
        print(f"\nWrote cleaned corpus -> {out_path}  (original untouched)")
    else:
        print("\n(dry run — nothing written. Re-run with --apply to produce a cleaned file.)")


if __name__ == "__main__":
    main()
