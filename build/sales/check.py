"""Daily sale check -> sales.js (window.SALES).

Two separate signals:
  items  : closet pieces that are actually marked down right now (matched by product handle in the brand's
           Shopify feed; brands without a feed cannot be checked item by item).
  events : brands running a real sale event, judged by a sitewide promotion on the homepage (a percentage
           off with sitewide/everything/event wording) or a large share of the whole catalogue marked down,
           or a clear jump against the brand's own 45-day baseline. A permanent sale rack does not count.
"""
import json, re, ssl, urllib.request, html, os, datetime, statistics, concurrent.futures as cf
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
H = {'User-Agent': UA, 'Accept': 'application/json,text/html,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}
TODAY = datetime.date.today().isoformat()
brands = [b for b in json.load(open('build/suggest/brands.json'))['brands'] if b['status'] == 'approved']
def jsload(p): return json.loads(open(p).read().split('= ', 1)[1].rstrip(';\n'))
pieces = jsload('data.js') + (jsload('suggestions.js') if os.path.exists('suggestions.js') else [])
by_handle = {}
for it in pieces:
    m = re.search(r'/products/([^/?#]+)', it['url'])
    if m: by_handle.setdefault(m.group(1).lower(), []).append(it)
HIST_PATH = 'build/sales/history.json'; hist = json.load(open(HIST_PATH)) if os.path.exists(HIST_PATH) else {}
def get(u, timeout=30): return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=timeout, context=ctx).read().decode('utf-8', 'ignore')
def feed(base):
    n = disc = 0; depths = []; items = {}
    for page in range(1, 7):
        d = json.loads(get(f'{base}/products.json?limit=250&page={page}'))
        prods = d.get('products', [])
        if not prods: break
        for p in prods:
            vs = [v for v in p.get('variants', []) if v.get('available')]
            if not vs: continue
            n += 1
            sale = [(float(v['price']), float(v['compare_at_price'])) for v in vs if v.get('compare_at_price') and float(v['compare_at_price']) > float(v['price'])]
            if sale:
                disc += 1; now, was = min(sale); depths.append(1 - now / was)
                for it in by_handle.get(p['handle'].lower(), []): items[it['id']] = dict(now=round(now, 2), was=round(was, 2), off=int(round((1 - now / was) * 100)))
    return dict(kind='feed', products=n, share=round(disc / n, 3) if n else 0, depth=round(statistics.median(depths), 2) if depths else 0, items=items)
def homepage(site):
    page = html.unescape(get(site)); text = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', page, flags=re.S); text = re.sub(r'<[^>]+>', ' ', text); text = re.sub(r'\s+', ' ', text)
    # A promotion counts only when the sitewide/event wording sits right next to the percentage, and it is
    # not an in-store-only, selected-styles, or sign-up offer.
    SITE = r'sitewide|site-wide|everything|all full[- ]price|entire (?:site|store)|storewide'
    EVENT = r"labor day|memorial day|black friday|cyber monday|presidents'? day|fourth of july|4th of july|end of season|semi-?annual|anniversary sale|friends (?:&|and) family|flash sale|(?:summer|winter|fall|spring) sale"
    EXCL = r'in[- ]store only|in person|selected|select styles|first (?:purchase|order)|newsletter|subscribe|closing|when you (?:sign up|join)'
    best = 0; event = None; sitewide = False
    for m in re.finditer(r'(\d{2})\s?%\s?off', text, re.I):
        win = text[max(0, m.start() - 90): m.end() + 90]
        if re.search(EXCL, win, re.I): continue
        ev = re.search(EVENT, win, re.I); sw = re.search(SITE, win, re.I)
        if sw or ev:
            sitewide = True; best = max(best, int(m.group(1)))
            if ev: event = ev.group(0).title()
    return dict(kind='homepage', maxoff=best, sitewide=sitewide, event=event)
def check(b):
    out = {'name': b['name']}
    try:
        f = feed(b['site'])
        if f['products']: out['feed'] = f
    except Exception: pass
    try: out['home'] = homepage(b['site'])
    except Exception as e: out['home_error'] = str(e)[:60]
    return out
results = list(cf.ThreadPoolExecutor(6).map(check, brands))
items = {}; events = {}; notes = {}
for r in results:
    name = r['name']; f = r.get('feed'); hm = r.get('home', {})
    if f: items.update(f['items'])
    share = f['share'] if f else None
    if share is not None:
        h = hist.setdefault(name, []); h.append([TODAY, share]); del h[:-45]
    base = statistics.median(x[1] for x in hist[name][:-1]) if share is not None and len(hist.get(name, [])) > 7 else None
    promo = bool(hm) and hm['maxoff'] >= 20 and (hm['sitewide'] or hm['event'])
    jump = base is not None and share >= 0.3 and share >= base * 2
    if promo or jump:
        events[name] = dict(off=hm['maxoff'] if promo and hm['maxoff'] else (int(round(f['depth'] * 100)) if f else 0), event=hm.get('event') if hm else None, why='promo' if promo else 'jump', checked=TODAY)
    notes[name] = dict(share=share, checked=bool(f), promo=promo)
json.dump(hist, open(HIST_PATH, 'w'))
open('sales.js', 'w').write('window.SALES = ' + json.dumps({'checked': TODAY, 'items': {str(k): v for k, v in items.items()}, 'events': events, 'brands': notes}, separators=(',', ':')) + ';\n')
byb = {}
for iid, v in items.items():
    it = next(i for i in pieces if i['id'] == iid); byb.setdefault(it['brand'], []).append(f"{it['name'][:34]} ${v['now']:.0f} was ${v['was']:.0f}")
print(f"closet pieces actually marked down: {len(items)}")
for b, L in sorted(byb.items()): print(f"  {b}: " + '; '.join(L[:4]) + (f" (+{len(L)-4} more)" if len(L) > 4 else ''))
print('sale events:', {k: (v['why'], v['off'], v['event']) for k, v in events.items()} or 'none')
print('brands checked item by item:', sum(1 for n in notes.values() if n['checked']), 'of', len(notes))
