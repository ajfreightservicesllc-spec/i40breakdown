#!/usr/bin/env python3
"""
Regenerate the missing i40breakdown.com shop pages.

- Output filenames are the EXACT live sitemap filenames (the 404 list), so there is
  zero chance of a new slug mismatch.
- Core data (name, phone, address, hours, rating, geo, website) comes from the
  enriched CSV. Service pills come from the live state-page cards (which carry the
  per-service flags the CSV lacks). Falls back gracefully when a source is missing.
- Writes to ./dry-run/  ONLY. Deploys nothing.
"""
import csv, re, os, html, glob

# Inputs live alongside this script so it runs from any machine (e.g. Google Drive), not just this PC.
PREP = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(PREP, "rigrescue_I40_cleaned.csv")
SCRATCH = PREP  # optional PREP/states/*.html enriches service pills; falls back to CSV flags if absent
FOUR04 = os.path.join(PREP, "i40breakdown_404_urls.txt")
OUT = os.path.join(PREP, "dry-run")

STATE = {'Arizona':'AZ','California':'CA','New Mexico':'NM','Texas':'TX','Oklahoma':'OK',
'Arkansas':'AR','Tennessee':'TN','North Carolina':'NC','Delaware':'DE','Georgia':'GA',
'Mississippi':'MS','New Jersey':'NJ','New York':'NY','Pennsylvania':'PA','South Carolina':'SC',
'Virginia':'VA','Illinois':'IL','Oregon':'OR','New Hampshire':'NH'}

def slug(t):
    return re.sub(r'-+','-', re.sub(r'[^a-z0-9]+','-', t.lower())).strip('-')

def esc(t):
    return html.escape(t, quote=True)

# ---- 1. missing filenames (authoritative) -------------------------------
missing = []
with open(FOUR04) as f:
    for line in f:
        u = line.strip()
        if u: missing.append(u.rsplit('/',1)[1])

# ---- 2. CSV core, keyed by generated filename + name/city fallback -------
gen, bykey = {}, {}
for r in csv.DictReader(open(CSV, encoding='utf-8')):
    st2 = STATE.get(r['state'].strip(), r['state'].strip().upper()[:2])
    fn = f"shop-{st2.lower()}-{slug(r['name'])}-{slug(r['city'])}.html"
    gen[fn] = (r, st2)
    bykey[(slug(r['name'])[:40], slug(r['city']), st2.lower())] = (r, st2)

# ---- 3. service flags from live state cards, keyed by filename -----------
FLAGS = ['road','t247','truck','rvs','reef','tire','eng','cool','trl','brk','elec']
cardflags = {}
for path in glob.glob(os.path.join(SCRATCH, 'states', '*.html')):
    page = open(path, encoding='utf-8').read()
    for block in re.findall(r'<article class="card"(.*?)</article>', page, re.S):
        m = re.search(r'data-href="([^"]+)"', block)
        if not m: continue
        fn = m.group(1)
        cardflags[fn] = {fl: (re.search(r'data-%s="1"'%fl, block) is not None) for fl in FLAGS}

# scraped full-data (for name/city/addr on the 15 stray shops with no CSV slug match)
scraped = {r['filename']: r for r in csv.DictReader(open(os.path.join(PREP,'missing-shops-FULL-DATA.csv'), encoding='utf-8'))}

TEMPLATE = open(os.path.join(PREP, 'page-template.html'), encoding='utf-8').read()

PILL_LABELS = [('road','Comes to you','hot'),('t247','24/7','hot247'),('truck','Truck specialist','grn'),
               ('tire','Tire',''),('eng','Engine',''),('cool','Cooling',''),('trl','Trailer',''),
               ('brk','Brakes',''),('elec','Electrical',''),('reef','Reefer',''),('rvs','RV','')]

def phone_tel(p):
    d = re.sub(r'[^\d]', '', p)
    return '+'+d if d else ''

def stars(rating):
    try: n = round(float(rating))
    except: return ''
    n = max(0, min(5, n))
    return '★'*n + '☆'*(5-n)

def render(fn):
    src = gen.get(fn)
    if not src:
        s = scraped.get(fn)
        if s:
            src = bykey.get((slug(s['name'])[:40], slug(s['city']), s['state'].lower()))
    if not src:
        # last-resort: derive from scraped record alone
        s = scraped.get(fn)
        if not s: return None
        r = {'name':s['name'],'phone':s['phone'],'website':s['website'],'full address':s['address'],
             'city':s['city'],'state':s['state'],'zip':(s['address'].split()[-1] if s['address'] else ''),
             'latitude':s['lat'],'longitude':s['lng'],'google rating':s['rating'],'review count':s['reviews'],
             'hours':'','is_24_7':'no','is_mobile':'no'}
        st2 = s['state'].upper()
    else:
        r, st2 = src

    name, city = r['name'].strip(), r['city'].strip()
    phone_disp = r['phone'].strip()
    tel = phone_tel(phone_disp)
    addr = r['full address'].strip()
    zipc = r.get('zip','').strip() or (addr.split()[-1] if addr else '')
    lat, lng = r.get('latitude','').strip(), r.get('longitude','').strip()
    rating = str(r.get('google rating','')).strip()
    reviews = str(r.get('review count','')).strip()
    website = r.get('website','').strip()
    hours = r.get('hours','').strip()
    # hours: strip python-list junk  Friday: ['8AM-6PM'] -> Friday: 8AM-6PM
    hours = re.sub(r"[\[\]'\"]", '', hours)
    if not hours or hours.lower()=='nan':
        hours = 'Call ahead for current hours.'

    fl = cardflags.get(fn) or {}
    if not fl:  # no state card -> derive from CSV booleans
        mob = str(r.get('is_mobile','')).strip().lower() in ('yes','true','1')
        t247 = str(r.get('is_24_7','')).strip().lower() in ('yes','true','1')
        fl = {k:False for k in FLAGS}; fl['road']=mob; fl['t247']=t247; fl['truck']=True
    mobile = fl.get('road') or fl.get('truck')

    # pills
    pills = []
    for key,label,cls in PILL_LABELS:
        if fl.get(key):
            if cls=='hot247':
                pills.append('<span class="pill hot"><span class="pdot"></span>24/7</span>')
            else:
                c = (' '+cls) if cls else ' '
                pills.append(f'<span class="pill{(" "+cls) if cls else " "}">{label}</span>')
    if not pills:
        pills = ['<span class="pill">Truck repair</span>']
    pills_html = ''.join(pills)

    # badge + tagline + what-we-do
    if mobile:
        badge = 'Mobile roadside service'
        tagline = f'Mobile I-40 breakdown service in {esc(city)}, {st2} - we roll out to your truck.'
    else:
        badge = 'Repair shop'
        tagline = f'I-40 breakdown repair in {esc(city)}, {st2} - truck, trailer and diesel, right off the interstate.'
    svc_words = [label.lower() for key,label,cls in PILL_LABELS
                 if fl.get(key) and key not in ('road','t247')]
    wwd = f'Right on the I-40 corridor in {esc(city)}, {st2}.'
    if fl.get('road'): wwd += ' We come to you for roadside breakdowns.'
    if svc_words: wwd += ' Services include: ' + ', '.join(svc_words) + '.'

    # rating block
    has_reviews = bool(reviews and reviews.lower() != 'nan' and reviews != '0')
    if rating and rating.lower()!='nan':
        if has_reviews:
            rate_div = f'<div class="rate">{stars(rating)} {rating} <span>({reviews} reviews)</span></div>'
            # aggregateRating is only schema-valid with a reviewCount >= 1
            jsonld_rating = f',"aggregateRating":{{"@type":"AggregateRating","ratingValue":{rating},"reviewCount":{reviews}}}'
        else:
            rate_div = f'<div class="rate">{stars(rating)} {rating}</div>'
            jsonld_rating = ''
    else:
        rate_div = ''
        jsonld_rating = ''
    jsonld_url = f'"url":"{esc(website)}",' if website else ''

    # call button + text link: omit when there is no phone number
    if tel:
        call_html = f'<a class="call" href="tel:{tel}">&#128222; Call {esc(phone_disp)}</a>'
        sms_html = f'<a class="txt" href="sms:{tel}">&#128172; Text us</a>'
    else:
        call_html = ''
        sms_html = ''

    page = TEMPLATE
    repl = {
        '{{FILENAME}}': fn,
        '{{NAME}}': esc(name),
        '{{CITY}}': esc(city),
        '{{STATE}}': st2,
        '{{STATE_FILE}}': st2.lower()+'.html',
        '{{PHONE_DISPLAY}}': esc(phone_disp),
        '{{PHONE_TEL}}': tel,
        '{{ADDRESS}}': esc(addr),
        '{{POSTAL}}': esc(zipc),
        '{{LAT}}': lat, '{{LNG}}': lng,
        '{{RATING}}': rating, '{{REVIEWS}}': reviews,
        '{{CALL_BUTTON}}': call_html,
        '{{SMS_LINK}}': sms_html,
        '{{BADGE}}': badge,
        '{{TAGLINE}}': tagline,
        '{{PILLS}}': pills_html,
        '{{WHATWEDO}}': wwd,
        '{{HOURS}}': esc(hours),
        '{{JSONLD_URL}}': jsonld_url,
        '{{JSONLD_RATING}}': jsonld_rating,
    }
    for k,v in repl.items():
        page = page.replace(k, v)
    # rating div line: replace the template's .rate line with rate_div (or remove)
    page = re.sub(r'<div class="rate">.*?</div>', rate_div, page, count=1)
    return page

os.makedirs(OUT, exist_ok=True)
written=0; skipped=[]
for fn in missing:
    p = render(fn)
    if p is None:
        skipped.append(fn); continue
    with open(os.path.join(OUT, fn), 'w', encoding='utf-8') as f:
        f.write(p)
    written += 1

print(f"Generated {written} pages into {OUT}")
print(f"Skipped (no data at all): {len(skipped)}")
for s in skipped: print("   ", s)
