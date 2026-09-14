import json, os, glob
items = json.load(open('build/items_raw.json'))
desc = json.load(open('build/desc_final.json'))
occ = {}
for p in sorted(glob.glob('build/occ/out_*.json')):
    try: occ.update(json.load(open(p)))
    except Exception as e: print('bad occ file', p, e)
VALID = {'teaching','dance','friend','hang','dressy','outdoors'}
DROP = {294, 295}
out = []; retagged = 0
for it in items:
    if it['id'] in DROP: continue
    full = f'images/full/{it["id"]:03d}.jpg'
    hi = os.path.exists(full)
    d = desc.get(str(it['id']), {})
    o = occ.get(str(it['id']))
    tags = [t for t in (o or {}).get('tags', []) if t in VALID]
    if tags: retagged += 1
    else: tags = it['occasions']
    out.append(dict(id=it['id'], brand=it['brand'], retailer=it['retailer'], name=it['name'],
        category=it['category'], color=it['color'], occasions=tags, why=(o or {}).get('why'), price=it['price'],
        colorDetail=it['colorDetail'], categoryDetail=it['categoryDetail'], url=it['url'],
        img=full if hi else it['thumb'], hi=hi,
        desc=d.get('desc'), details=d.get('details') or [], fabric=d.get('fabric')))
with open('data.js','w') as f:
    f.write('window.CLOSET = ' + json.dumps(out, ensure_ascii=False, separators=(',',':')) + ';\n')
print(len(out), 'items,', sum(1 for o in out if o['hi']), 'hi-res,', sum(1 for o in out if not o['hi']), 'thumbnail-only,', retagged, 'retagged,', sum(1 for o in out if o['desc']), 'with description')
import collections; print('thumb-only by retailer', dict(collections.Counter(o['retailer'] for o in out if not o['hi'])))
print('tag counts', dict(collections.Counter(t for o in out for t in o['occasions'])))
