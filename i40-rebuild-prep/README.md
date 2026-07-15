# i40breakdown.com — Rebuild Prep

Prep work for regenerating the ~1,012 missing shop pages. **Nothing on the live site was changed** — everything here was produced by read-only scraping of the live site plus analysis of the 404 list.

## Files in this folder

| File | What it is |
|------|-----------|
| `page-template.html` | Exact copy of a real live shop page, turned into a fill-in template with `{{PLACEHOLDER}}` markers. Matches the live design pixel-for-pixel. |
| `TEMPLATE-NOTES.md` | Field-by-field guide: every placeholder, and the rules for optional fields (rating / website / hours / services). |
| `missing-shops-FULL-DATA.csv` | **The recovered data source.** 997 of the 1,012 missing shops, with name, city, state, address, phone, website, lat/lng, rating, review count, and services — scraped from the live state pages. This is effectively the enriched CSV, rebuilt from the live site. |
| `404-shop-checklist.csv` | Simple checklist: state, city, shop name, filename, URL for all 1,012 missing pages. |
| `404-by-state.txt` | Count of missing pages per state, with % gap. |

## Key finding

The "missing" shop data is **not lost**. The live **state pages** (`nc.html`, `tn.html`, …) embed the full record for every shop — including the ones whose individual pages 404 — inside `<article class="card" data-*>` attributes. That data was scraped back out.

- **997 / 1,012** missing shops recovered with full data (100% have address + geo, 97% phone, 95% rating).
- **15 / 1,012** could not be recovered — they belong to non-I-40 states (DE, IL, MS, NJ, PA, SC, VA) that have **no state page** at all. These look like stray/mis-tagged entries and are listed at the bottom of the checklist as `(no state-page data)`.

## Data completeness (of the 997 recovered)

| Field | Coverage |
|-------|----------|
| Address | 997/997 (100%) |
| Geo (lat/lng) | 997/997 (100%) |
| Phone | 971/997 (97%) |
| Rating + reviews | 952/997 (95%) |
| Website | 653/997 (66%) — optional on the page |
| Services | 681/997 (68%) — optional on the page |

## What's NOT done (waiting on your go)

No pages have been generated and nothing has been deployed. When you're ready, the rebuild is:
1. Feed `missing-shops-FULL-DATA.csv` through a generator using `page-template.html`.
2. Produce 997 flat `shop-*.html` files with filenames **identical** to the sitemap URLs.
3. Deploy **add-only** (never delete the 1,059 live pages).
4. Decide separately what to do with the 15 stray-state shops.
