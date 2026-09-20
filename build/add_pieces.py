"""Add owner-requested pieces from Shopify stores to build/extras.json (ids continue after the last extra).

Usage: python3 build/add_pieces.py   (edit the T list below, then run make_data.py)
Retries politely on HTTP 429, which Shopify returns after a burst of requests from one address.
"""
import json, ssl, urllib.request, re, html, io, time, sys
from PIL import Image
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1', 'Accept': 'application/json,image/*,*/*'}
def get(u, tries=12):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40, context=ctx).read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1: print(f'  429 from {u.split("/")[2]}, waiting 60s'); time.sleep(60); continue
            raise
def clean(s): return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()

T = [
 dict(id=433, url='https://us.boden.com/products/women-raglan-embroidered-top-mid-blue-t2183blu', brand='Boden', retailer='Boden',
      name='Raglan Embroidered Top', category='Shirts & Blouses', categoryDetail='Embroidered blouse', color='Blue', colorDetail='Mid Blue',
      occasions=['teaching', 'friend', 'hang'], why='cotton and linen breathe, raglan sleeves move; embroidery makes it a teaching-day blouse',
      fabric='Cotton and linen', extra_details=['Owner-requested 2026-09-20', 'On sale at Boden that day: $133, was $190'],
      note=''),
 dict(id=434, url='https://us.toa.st/products/washed-black-denim-skirt-carbon-black', brand='TOAST', retailer='TOAST',
      name='Washed Black Denim Skirt', category='Skirts', categoryDetail='A-line denim skirt', color='Black', colorDetail='Carbon Black',
      occasions=['teaching', 'hang', 'friend'], why='heavy washed denim in an A-line, lower-calf length; the shape she keeps hearting, in a skirt',
      fabric='100% cotton denim, with recycled and regenerative cotton', extra_details=['Owner-requested 2026-09-20', 'Sizes 4 to 18', 'Lower-calf length, regular fit, on the waist'],
      note=''),
]
extras = json.load(open('build/extras.json')); ids = {t['id'] for t in T}
extras = [e for e in extras if e['id'] not in ids]
for t in T:
    d = json.loads(get(t['url'].split('?')[0] + '.js'))
    price = d['price'] / 100
    desc = clean(d.get('description', ''))
    desc = re.split(r'\s###\s|Size & Fit', desc)[0].strip()[:600]
    details = list(t['extra_details'])
    for pat in [r'\d{1,3}% [A-Za-z ]+?(?=[,.;]|$)', r'Machine wash[^.]*\.', r'Made in [A-Z][a-z]+']:
        for m in re.findall(pat, clean(d.get('description', ''))):
            m = m.strip().rstrip('.')
            if m and m not in details and len(details) < 8: details.append(m)
    src = d['images'][0]; src = ('https:' + src) if src.startswith('//') else src
    im = Image.open(io.BytesIO(get(src.split('?')[0] + '?width=1000'))); im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[-1]); im = bg
    else: im = im.convert('RGB')
    im.thumbnail((900, 900)); path = f"images/full/{t['id']}.jpg"; im.save(path, 'JPEG', quality=84, optimize=True)
    extras.append(dict(id=t['id'], brand=t['brand'], retailer=t['retailer'], name=t['name'], category=t['category'], color=t['color'], occasions=t['occasions'], why=t['why'], price=price,
                       colorDetail=t['colorDetail'], categoryDetail=t['categoryDetail'], url=t['url'], img=path, hi=True, desc=desc, details=details, fabric=t['fabric'], note=t['note']))
    print(t['id'], t['brand'], t['name'], '$', price, '| photo', im.size)
extras.sort(key=lambda e: e['id'])
json.dump(extras, open('build/extras.json', 'w'), indent=1, ensure_ascii=False)
print(len(extras), 'extras written')
