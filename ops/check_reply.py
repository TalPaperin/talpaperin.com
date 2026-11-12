#!/usr/bin/env python3
"""Gate for every outgoing prospect reply. Run it on the reply text BEFORE sending:

    python3 ops/check_reply.py reply.json      # JSON with "body_text"
    python3 ops/check_reply.py reply.txt       # or plain text
    python3 ops/check_reply.py reply.json --other     # DealMentor / HireMatch reply (no Tal site link)

Exit code 0 = clean, 1 = blocked (the reasons are printed). A blocked reply is rewritten, never sent.
The lists come from ops/positioning.md, ops/explee_rules.md and CLAUDE.md. Add to them when Tal
corrects a reply, so the same mistake cannot go out twice.
"""
import json, re, sys

BANNED = [
    # positioning (ops/positioning.md, Tal 2026-11-12)
    "not an agency", "one person", "one senior person", "just a person", "solo",
    "does the selling himself", "marketing agency",
    # cheapening offers (ops/explee_rules.md)
    "a few short ideas", "a few ideas", "send you some ideas", "free audit",
    # yearly pricing (CLAUDE.md: fees are monthly only)
    "per year", "a year", "annually", "$144",
    # de-slop (CLAUDE.md)
    "delve", "leverage", "robust", "seamless", "elevate", "unlock", "unleash", "harness", "foster",
    "landscape", "realm", "tapestry", "testament", "pivotal", "crucial", "vital", "game-changer",
    "cutting-edge", "supercharge", "turbocharge", "let that sink in", "the bottom line is",
    "at the end of the day", "low-hanging fruit", "move the needle", "deep dive", "circle back",
]
ALLOWED_LINKS = ("https://talpaperin.com", "https://calendly.com/ksw/15min")

def check(text, require_site=True):
    problems = []
    low = text.lower()
    for phrase in BANNED:
        if re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", low):
            problems.append('banned wording: "%s"' % phrase)
    if re.search("[‐-―]", text):
        problems.append("em or en dash")
    if re.search("[‘’“”…]", text):
        problems.append("curly quote or ellipsis character")
    links = re.findall(r"https?://[^\s)>\]]+", text)
    site = [l for l in links if "calendly.com" not in l]
    if len(site) > 1:
        problems.append("more than one site link (%d). One link only: https://talpaperin.com" % len(site))
    if require_site:
        if not any(l.rstrip("/.,") == "https://talpaperin.com" for l in links):
            problems.append("no site link. Every Talpaperin reply carries https://talpaperin.com (Tal, 2026-11-12)")
        if "recommendations" not in low or "case studies" not in low:
            problems.append('say what the site holds: "client recommendations and case studies"')
    for l in links:
        if not l.rstrip("/.,").startswith(ALLOWED_LINKS) and "talpaperin.com/pricing" not in l and "thedealmentor.ai" not in l and "linkedin.com/in/talpaperin" not in l:
            problems.append("unexpected link: %s" % l)
    return problems

if __name__ == "__main__":
    raw = open(sys.argv[1], encoding="utf-8").read()
    try:
        raw = json.loads(raw).get("body_text", raw)
    except Exception:
        pass
    # Talpaperin replies must carry the site link. Pass --other for DealMentor / HireMatch replies,
    # or --no-site for the rare Talpaperin reply where a link is wrong (a decline acknowledgement).
    probs = check(raw, require_site=not any(a in ("--other", "--no-site") for a in sys.argv[2:]))
    if probs:
        print("BLOCKED:")
        for p in probs:
            print(" -", p)
        sys.exit(1)
    print("clean")
