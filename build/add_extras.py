import json, re
raw = json.load(open('build/nasrin_raw.json'))
CAT = {'jumpsuit': 'Jumpsuits & Rompers', 'jumpsuits': 'Jumpsuits & Rompers', 'dress': 'Dresses', 'dresses': 'Dresses', 'pants': 'Jeans', 'top': 'Sweaters & Knitwear'}
COLOR = {396: ('Multi/Print', 'Butterfly print on black'), 397: ('Black', 'Black'), 398: ('Green', 'Teal corduroy'), 399: ('Black', 'Black'),
         400: ('Purple', 'Fig'), 401: ('Black', 'Black'), 402: ('Green', 'Teal & Peacock'), 403: ('Purple', 'Currant print'),
         404: ('Red', 'Currant print'), 405: ('Green', 'Olive'), 406: ('Multi/Print', 'Forest print'), 407: ('Multi/Print', 'Flora print on black'),
         408: ('Red', 'Heart print'), 409: ('Denim', 'Dark wash denim'), 410: ('Denim', 'Dark wash denim'), 411: ('Black', 'Paloma print, black & white')}
TAGS = {
 396: (['teaching','dance','friend'], 'soft stretchy cotton, elastic waist, wide cropped leg, dark butterfly print'),
 397: (['teaching','dance','friend'], 'stretchy lyocell, black, elastic waist, wide cropped leg'),
 398: (['teaching','friend','hang'], 'stretch corduroy, cosy fall weight, teal'),
 399: (['teaching','dressy','friend'], 'matte cupro with no stretch, collared and belted, office polish'),
 400: (['teaching','friend','hang'], 'cupro utility jumpsuit, long sleeves, relaxed full-length leg'),
 401: (['teaching','dressy','friend'], 'stretch wrinkle-resistant fabric, boatneck, full wide leg, desk to dinner'),
 402: (['dance','friend','hang'], 'breathable linen, roomy wide leg, teal and peacock'),
 403: (['dressy','friend'], 'flowy lined chiffon maxi, mock neck, fitted waist, wedding-guest dressy'),
 404: (['teaching','friend','dressy'], 'collared sleeveless midi, belted, no stretch, currant print'),
 405: (['teaching','dressy','friend'], 'silky cupro midi, mock neck, tie belt, olive'),
 406: (['dance','dressy','friend'], 'true wrap maxi, lightweight flowy lined skirt, dark forest print'),
 407: (['teaching','dance','friend'], '100% cotton, belted A-line midi, dark floral print, pockets'),
 408: (['dance','dressy','friend'], 'true wrap maxi, flowy lined skirt, bold heart print'),
 409: (['hang','friend'], 'structured non-stretch denim, barrel leg, high waist'),
 410: (['teaching','friend','hang'], 'dark non-stretch denim, subtle wide leg, high waist, polished'),
 411: (['teaching','hang','friend'], '100% cotton cardigan, relaxed fit, black and white print'),
}
FAB = re.compile(r'cotton|lyocell|cupro|corduroy|linen|chiffon|denim|wool|viscose|rayon|silk|polyester', re.I)
out = []
for r in raw:
    iid = r['id']; lines = [l.strip() for l in r['desc'].split('\n') if l.strip()]
    # prose: lines after "Designer's Note:" until "The Details:" or the first short bullet
    prose = []; details = []; mode = 'prose'
    for l in lines:
        low = l.lower()
        if low.startswith("designer's note"): continue
        if low.startswith('the details'): mode = 'details'; continue
        if low.startswith("model's measurements") or re.match(r'^(height|bust|waist|hips?):', low) or 'is wearing' in low: mode = 'skip'; continue
        if mode == 'skip': continue
        if l.startswith('*') or 'style with our' in low or low.startswith('leila top') or low in ('s', 'tyle with our'): continue
        if l.endswith('.') and len(l) > 60 and mode == 'prose': prose.append(l)
        elif len(l) <= 70: details.append(l.rstrip('.'))
        elif mode == 'prose': prose.append(l)
    if not prose:  # descriptions without a "The Details" header: first long line is prose
        prose = [l for l in lines[1:2]]
    desc = ' '.join(prose).replace('  ', ' ').strip()
    desc = re.sub(r'\s+/\s*for a monochromatic look\.?', '', desc)
    if r['compare_at'] and r['compare_at'] > r['price']:
        details.append(f"On sale, was ${r['compare_at']:.0f}")
    seen = set(); det = []
    for d in details:
        if d.lower() not in seen and not d.lower().startswith('original') or 'print' in d.lower():
            seen.add(d.lower()); det.append(d)
    fabric = next((d for d in det if FAB.search(d) and 'print' not in d.lower()), None)
    color, cdetail = COLOR[iid]; tags, why = TAGS[iid]
    out.append(dict(id=iid, brand='Mixed by Nasrin', retailer='Mixed by Nasrin', name=r['title'],
        category=CAT[r['type'].lower()], color=color, occasions=tags, why=why, price=r['price'],
        colorDetail=cdetail, categoryDetail=r['type'], url=r['url'], img=r['img'], hi=True,
        desc=desc or None, details=det[:8], fabric=fabric))
FIX = {
 397: {'desc': lambda d: d.replace('little back dress', 'little black dress')},
 401: {'fabric': 'Medium weight, stretchy, wrinkle-resistant fabric'},
 402: {'fabric': 'Breathable linen'},
 407: {'desc': "Chic, modern, feminine, powerful. The Rachel Dress in Flora has just the right balance of structure and flow, with pockets that make it functional and an invisible zipper neckline that allows you to transition this piece from desk to dinner. Crafted from 100% cotton, this dress is an iconic piece for the trailblazing woman who works hard, dresses well, and somehow looks effortless doing it all.",
       'details': ['Hand-drawn, original Mixed print', '100% cotton', 'Invisible front zipper', 'Fabric finished belt', 'Pockets', 'Wide hem detailing', 'Runs large; size down'], 'fabric': '100% cotton'},
 409: {'desc': lambda d: re.sub(r'\s*Style with our\s*$', '', d).strip(), 'details': lambda L: [x for x in L if 'monochromatic' not in x]},
 410: {'desc': lambda d: re.sub(r'\s*S(tyle with our)?\s*$', '', d).strip(), 'details': lambda L: [x for x in L if 'monochromatic' not in x]},
}
for o in out:
    for k, v in FIX.get(o['id'], {}).items():
        o[k] = v(o[k]) if callable(v) else v
    o['desc'] = re.sub(r'\s+', ' ', o['desc']).replace(' .', '.').strip()
json.dump(out, open('build/extras.json', 'w'), indent=1, ensure_ascii=False)
for o in out: print(o['id'], o['category'], '|', o['color'], '|', o['fabric'], '|', o['desc'][:70], '|', o['details'][:4])
