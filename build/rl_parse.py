import json, os, re, html, ssl, urllib.request, io
from PIL import Image
items=[i for i in json.load(open('build/items_raw.json')) if i['retailer']=='Ralph Lauren']
bd=json.load(open('build/browser_desc.json')); h=json.load(open('build/hires_urls.json'))
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
def clean(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s))).strip()
FAB=re.compile(r'\d{1,3}%\s*(?:organic |recycled |merino |pima |virgin )?(?:cotton|wool|linen|silk|cashmere|viscose|rayon|lyocell|modal|polyester|nylon|elastane|spandex|polyamide|acrylic|alpaca|leather|cupro|tencel)', re.I)
parsed=0; imgs=0
for it in items:
    p=f'build/rl_pages/{it["id"]:03d}.html'
    if not os.path.exists(p): continue
    page=open(p).read()
    d=re.search(r'class="pdp-details-description-in[^"]*"\s*>(.*?)</div>', page, re.S)
    desc=clean(d.group(1)) if d else None
    lis=[]
    for ul in re.findall(r'<ul[^>]*>(.*?)</ul>', page, re.S):
        cand=[clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', ul, re.S)]
        if cand and any(FAB.search(c) for c in cand) and not any('Off' in c or 'Sale' in c for c in cand):
            out=[]
            for c in cand:
                c=re.sub(r'^(?:Product Details\s*)+(?:Details\s*)?', '', c).strip()
                if not c or len(c)>140 or c.lower().startswith(('model is','style number','imported','size ')) or 'dress length is taken' in c.lower(): continue
                out.append(c)
            lis=out; break
    if desc or lis: bd[str(it['id'])]={'desc':desc,'lis':lis}; parsed+=1
    og=re.search(r'property="og:image"\s+content="([^"]+)"', page)
    if og and not os.path.exists(f'images/full/{it["id"]:03d}.jpg'):
        u=html.unescape(og.group(1))
        try:
            data=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'image/*,*/*'}),timeout=30,context=ctx).read()
            im=Image.open(io.BytesIO(data)).convert('RGB'); im.thumbnail((900,900)); im.save(f'images/full/{it["id"]:03d}.jpg','JPEG',quality=82,optimize=True)
            h[str(it['id'])]={'img':u,'err':None}; imgs+=1
        except Exception as e: print('img fail', it['id'], str(e)[:50])
json.dump(bd,open('build/browser_desc.json','w'),indent=0,ensure_ascii=False); json.dump(h,open('build/hires_urls.json','w'),indent=1)
print('RL parsed', parsed, '| new RL images', imgs)
print('sample', bd[str(items[0]['id'])])
