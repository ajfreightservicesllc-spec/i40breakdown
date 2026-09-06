#!/usr/bin/env python3
"""Refresh <lastmod> in public/sitemap.xml for pages whose content changed.

lastmod-store.json maps filename -> {hash: sha256 of file bytes, lastmod}.
A page's lastmod is bumped to today only when its sha256 differs from the
stored one, so untouched pages keep their real dates. Never adds or removes
sitemap URLs (see audit_links.py for the freeze check).

Usage:  python3 i40-deploy/update_lastmod.py            # apply
        python3 i40-deploy/update_lastmod.py --dry-run  # report only
"""
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, "public")
STORE = os.path.join(HERE, "lastmod-store.json")
SITEMAP = os.path.join(PUBLIC, "sitemap.xml")
HOST = "https://www.i40breakdown.com/"


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    dry = "--dry-run" in sys.argv
    today = datetime.date.today().isoformat()
    with open(STORE, encoding="utf-8") as fh:
        store = json.load(fh)
    with open(SITEMAP, encoding="utf-8") as fh:
        sm = fh.read()

    changed = []
    for fname, rec in store.items():
        path = os.path.join(PUBLIC, fname)
        if not os.path.exists(path):
            print("WARNING: in store but not on disk:", fname)
            continue
        h = sha(path)
        if h != rec["hash"]:
            changed.append(fname)
            rec["hash"] = h
            rec["lastmod"] = today
            loc = HOST + ("" if fname == "index.html" else fname)
            pat = re.compile(r"(<loc>" + re.escape(loc) + r"</loc><lastmod>)[^<]*(</lastmod>)")
            sm, n = pat.subn(r"\g<1>" + today + r"\g<2>", sm)
            if n != 1:
                print("WARNING: sitemap entry not found for", fname)

    print(f"{len(changed)} changed page(s):")
    for f in changed:
        print(" -", f)
    if dry or not changed:
        return 0
    with open(STORE, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=0)
        fh.write("\n")
    with open(SITEMAP, "w", encoding="utf-8") as fh:
        fh.write(sm)
    print("lastmod-store.json and sitemap.xml updated (URL count unchanged).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
