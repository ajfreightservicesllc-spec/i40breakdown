# Template field guide — `page-template.html`

Source of truth: a live page (`shop-nc-ac-auto-winston-salem.html`) plus 3 other live pages sampled to confirm optional-field behavior. The template reproduces the live design exactly (dark theme, mobile-first, `max-width:560px`).

## Filename & URL rule (the bug that caused the 404s — DO NOT repeat)

The individual page filename **must be byte-for-byte identical** to what the sitemap and the state/city page links already use:

```
shop-{state}-{name-slug}-{city-slug}.html
```

- `{state}` = lowercase 2-letter (nc, tn, ar, …)
- `{name-slug}` and `{city-slug}` = lowercased, special characters handled the SAME way they already are in the live sitemap.
- The `filename` column in `missing-shops-FULL-DATA.csv` is copied straight from the live sitemap — **use it verbatim as the output filename.** That alone guarantees no new mismatch.

## Placeholders

| Placeholder | Source (CSV column) | Example |
|-------------|--------------------|---------|
| `{{FILENAME}}` | `filename` | `shop-nc-ac-auto-winston-salem.html` |
| `{{NAME}}` | `name` | `AC Auto` |
| `{{CITY}}` | `city` | `Winston-Salem` |
| `{{STATE}}` | `state` | `NC` |
| `{{STATE_FILE}}` | derive from state | `nc.html` |
| `{{PHONE_DISPLAY}}` | `phone` | `+1 336-717-4808` |
| `{{PHONE_TEL}}` | `phone`, digits only + leading `+` | `+13367174808` |
| `{{ADDRESS}}` | `address` | `2425 W Clemmonsville Rd, Winston-Salem, NC 27127` |
| `{{POSTAL}}` | last token of address | `27127` |
| `{{LAT}}` / `{{LNG}}` | `lat` / `lng` | `36.0320958` / `-80.31989999` |
| `{{RATING}}` | `rating` | `4.6` |
| `{{REVIEWS}}` | `reviews` | `995` |
| `{{STARS}}` | render from rating | `★★★★★` |

## Optional-field rules (confirmed by comparing live pages)

### Rating (`.rate` div + JSON-LD `aggregateRating`)
- **Has rating** → emit `<div class="rate">★★★★★ {{RATING}} <span>({{REVIEWS}} reviews)</span></div>` AND include in JSON-LD:
  `,"aggregateRating":{"@type":"AggregateRating","ratingValue":{{RATING}},"reviewCount":{{REVIEWS}}}`
- **No rating** → OMIT the `.rate` div entirely (live pages leave a blank line) and omit the JSON-LD `aggregateRating` key.
- `{{JSONLD_RATING}}` in the template = that aggregateRating fragment, or empty string.

### Website (JSON-LD `url` only — no visible link on the page)
- **Has website** → `{{JSONLD_URL}}` = `"url":"https://…/",`
- **No website** → `{{JSONLD_URL}}` = empty string.

### Hours
- **Has hours** → full string, e.g. `Friday: 7:30AM-6PM; Monday: 7:30AM-6PM; …`
- **No hours** (all recovered rows — hours were NOT in state-page data) → use the live fallback: `Call ahead for current hours.`

### Services → `{{PILLS}}` and `{{WHATWEDO}}`
Services come from the `services` column (`|`-separated), derived from the state-page service flags.
- Pills markup: one `<span class="pill …">LABEL</span>` per service.
  - `Comes to you` (mobile/roadside) → `pill hot`; also add a `pill hot` `24/7` if flagged.
  - `Truck specialist` → `pill grn`.
  - Everything else (Tire, Engine, Cooling, Brakes, Electrical, Trailer, Reefer, RV) → plain `pill`.
- **No services** → single `<span class="pill">Truck repair</span>` (matches live fallback page).

### Badge & tagline (mobile vs fixed shop)
- **Mobile / roadside** (has "Comes to you"): badge `Mobile roadside service`; tagline `Mobile I-40 breakdown service in {{CITY}}, {{STATE}} - we roll out to your truck.`; "What we do" lists services.
- **Fixed shop**: badge `Repair shop`; tagline `I-40 breakdown repair in {{CITY}}, {{STATE}} - truck, trailer and diesel, right off the interstate.`; "What we do" = `Right on the I-40 corridor in {{CITY}}, {{STATE}}.`

## Constant across all pages
- Google Analytics tag: `G-M0PYD8479W`
- JSON-LD `@type`: `AutoRepair`
- Back link, claim link, footer all point to `{{STATE_FILE}}` / `index.html`.
