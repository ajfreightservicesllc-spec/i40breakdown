#!/usr/bin/env python3
"""Indexation-recovery guardrails for i40breakdown.com.

Checks, without changing anything:
  1. Sitemap freeze  - sitemap.xml must hold exactly FROZEN_SITEMAP_URLS <loc>
                       entries (the URL count on 2026-09-06). Adding pages while
                       sampled indexation is below target is prohibited.
  2. Sitemap parity  - every sitemap URL exists on disk; every HTML file on disk
                       (except claim.html) is in the sitemap.
  3. Crawl depth     - every HTML page is reachable by real <a href> links within
                       MAX_DEPTH clicks of index.html.
  4. Orphans         - every HTML page has at least one inbound anchor link.

Run from anywhere:  python3 i40-deploy/audit_links.py
Exit status 0 = all checks pass, 1 = something needs fixing.
"""
import collections
import os
import re
import sys

FROZEN_SITEMAP_URLS = 2107   # frozen 2026-09-06; change only with Rufus's typed approval
MAX_DEPTH = 2
HOST = "https://www.i40breakdown.com/"

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
HREF = re.compile(r'<a\s[^>]*href="([^"#?]+)', re.I)


def main():
    files = sorted(f for f in os.listdir(PUBLIC) if f.endswith(".html"))
    fileset = set(files)
    out = {}
    for f in files:
        with open(os.path.join(PUBLIC, f), encoding="utf-8", errors="ignore") as fh:
            s = fh.read()
        links = set()
        for h in HREF.findall(s):
            h = h.replace(HOST, "").lstrip("/") or "index.html"
            if h in fileset:
                links.add(h)
        out[f] = links

    inbound = collections.Counter()
    for links in out.values():
        for t in links:
            inbound[t] += 1

    depth = {"index.html": 0}
    q = collections.deque(["index.html"])
    while q:
        u = q.popleft()
        for v in out[u]:
            if v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)

    with open(os.path.join(PUBLIC, "sitemap.xml"), encoding="utf-8") as fh:
        sm_raw = re.findall(r"<loc>([^<]+)</loc>", fh.read())
    sm = {(u.replace(HOST, "") or "index.html") for u in sm_raw}

    problems = []
    if len(sm_raw) != FROZEN_SITEMAP_URLS:
        problems.append(f"SITEMAP FREEZE BROKEN: {len(sm_raw)} URLs, frozen at {FROZEN_SITEMAP_URLS}")
    missing = sorted(sm - fileset)
    if missing:
        problems.append(f"{len(missing)} sitemap URLs have no file on disk: {missing[:5]}")
    extra = sorted(fileset - sm - {"claim.html"})
    if extra:
        problems.append(f"{len(extra)} HTML files on disk are not in the sitemap: {extra[:5]}")
    deep = sorted(f for f in files if depth.get(f, 99) > MAX_DEPTH)
    if deep:
        problems.append(f"{len(deep)} pages are more than {MAX_DEPTH} clicks from the homepage: {deep[:5]}")
    orphans = sorted(f for f in files if inbound[f] == 0)
    if orphans:
        problems.append(f"{len(orphans)} pages have zero inbound links: {orphans[:5]}")

    hist = collections.Counter(depth.get(f, "unreached") for f in files)
    print(f"HTML files on disk: {len(files)}   sitemap URLs: {len(sm_raw)} (frozen at {FROZEN_SITEMAP_URLS})")
    print("click depth from homepage:", dict(sorted(hist.items(), key=lambda kv: str(kv[0]))))
    print(f"homepage outbound links: {len(out['index.html'])}")
    if problems:
        print("\nFAIL")
        for p in problems:
            print(" -", p)
        return 1
    print("\nOK: sitemap frozen, parity exact, every page within "
          f"{MAX_DEPTH} clicks, no orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
