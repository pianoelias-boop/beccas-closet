"""Daily sale check. Writes sales.js (window.SALES) and keeps a rolling history per brand.

Brands with a Shopify feed: share of in-stock products marked down and the median depth.
Others: a conservative scan of the homepage for a sitewide promotion.
A brand is flagged when its discounted share is clearly above its own normal, so brands with a
permanent sale rack do not stay lit forever.
"""
import json, re, ssl, urllib.request, html, os, datetime, statistics, concurrent.futures as cf, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); os.chdir(ROOT)
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
H = {'User-Agent': UA, 'Accept': 'application/json,text/html,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.9'}
TODAY = datetime.date.today().isoformat()
brands = json.load(open('build/suggest/brands.json'))['brands']
closet_brands = {i['retailer'] for i in json.loads(open('data.js').read().split('= ', 1)[1].rstrip(';\n'))}
HIST_PATH = 'build/sales/history.json'; hist = json.load(open(HIST_PATH)) if os.path.exists(HIST_PATH) else {}
def get(u, timeout=30): return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=timeout, context=ctx).read().decode('utf-8', 'ignore')
def feed(base):
    n = disc = 0; depths = []
    for page in range(1, 6):
        d = json.loads(get(f'{base}/products.json?limit=250&page={page}'))
        prods = d.get('products', [])
        if not prods: break
        for p in prods:
            vs = [v for v in p.get('variants', []) if v.get('available')]
            if not vs: continue
            n += 1; v = vs[0]
            if v.get('compare_at_price') and float(v['compare_at_price']) > float(v['price']):
                disc += 1; depths.append(1 - float(v['price']) / float(v['compare_at_price']))
    return dict(kind='feed', products=n, share=round(disc / n, 3) if n else 0, depth=round(statistics.median(depths), 2) if depths else 0)
def homepage(site):
    page = html.unescape(get(site)); text = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', page, flags=re.S); text = re.sub(r'<[^>]+>', ' ', text); text = re.sub(r'\s+', ' ', text)
    pct = [int(x) for x in re.findall(r'(\d{2})\s?%\s?off', text, re.I)]
    sitewide = bool(re.search(r'sitewide|site-wide|everything|all full[- ]price|entire (site|store)|storewide', text, re.I))
    event = re.search(r"labor day|memorial day|black friday|cyber monday|presidents'? day|fourth of july|4th of july|end of season|semi-?annual|anniversary sale|friends (&|and) family", text, re.I)
    return dict(kind='homepage', maxoff=max(pct) if pct else 0, sitewide=sitewide, event=event.group(0).title() if event else None)
def check(b):
    try:
        r = feed(b['site'])
        if r['products'] == 0: raise ValueError('empty feed')
    except Exception:
        try: r = homepage(b['site'])
        except Exception as e: return b['name'], dict(kind='error', error=str(e)[:60])
    return b['name'], r
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for name, r in ex.map(check, [b for b in brands if b['status'] == 'approved']):
        out[name] = r
sales = {}
for name, r in out.items():
    if r['kind'] == 'feed':
        h = hist.setdefault(name, []); h.append([TODAY, r['share']]); del h[:-45]
        base = statistics.median(x[1] for x in h[:-1]) if len(h) > 7 else None
        on = (r['share'] >= 0.2 and (base is None and r['share'] >= 0.3 or base is not None and r['share'] >= max(0.2, base * 1.5))) or (r['share'] >= 0.5)
        sales[name] = dict(on=bool(on), share=r['share'], off=int(round(r['depth'] * 100)) if on else 0, kind='feed', checked=TODAY)
    elif r['kind'] == 'homepage':
        on = r['sitewide'] and r['maxoff'] >= 20
        sales[name] = dict(on=bool(on), off=r['maxoff'] if on else 0, event=r['event'], kind='homepage', checked=TODAY)
    else:
        sales[name] = dict(on=False, kind='error', checked=TODAY)
json.dump(hist, open(HIST_PATH, 'w'))
open('sales.js', 'w').write('window.SALES = ' + json.dumps({'checked': TODAY, 'brands': sales}, separators=(',', ':')) + ';\n')
flagged = [f"{k} ({v.get('off')}% off)" for k, v in sales.items() if v['on']]
print(f"checked {len(sales)} brands; on sale now: {flagged or 'none'}")
for k, v in sorted(sales.items(), key=lambda kv: -(kv[1].get('share') or 0))[:12]:
    print(f"  {k:24s} {v['kind']:8s} share {v.get('share', '-')} off {v.get('off', 0)} {'ON' if v['on'] else ''} {v.get('event') or ''}")
