"""Add the ten merino tanks (curated 2026-09-15) to build/extras.json as ids 412-421."""
import json, ssl, urllib.request, re, html, io, shutil
from PIL import Image
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36','Accept':'application/json,image/*,*/*'}
def clean(s): return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s or ''))).strip()
T=[
 (412,'Unbound Merino','https://unboundmerino.com/products/womens-merino-rib-scoop-neck-tank','M1',"Women's Merino Rib Scoop Neck Tank",70,
   'Designed with a touch of added stretch, this ribbed essential delivers Merino performance in a fitted silhouette made for easy layering, or for wearing on its own.',
   ['96% merino wool, 4% spandex','210 gsm, 16.5 micron ultrafine merino','Fitted rib; runs slightly small, size up for a regular fit','Machine wash cold, lay flat to dry'],'96% merino wool, 4% spandex',
   ['dance','friend','hang'],'ultrafine merino rib with stretch, wicks and resists odour, fitted, black',
   'The most "real top" of the merino tanks: a fitted rib that hides damp and passes for going out. The heaviest of the ten, so best for cooler rooms.'),
 (413,'Unbound Merino','https://unboundmerino.com/products/womens-relaxed-merino-scoop-neck-tank','M3',"Women's Relaxed Merino Scoop Neck Tank",85,
   'Crafted from a lightweight Merino jersey, this soft tank features a scooped neckline and an easy, relaxed fit that sits away from the body. Ideal for warm days and effortless layering.',
   ['100% merino wool jersey','175 gsm, 16.5 micron ultrafine merino','Relaxed fit with extra room in chest and waist','Front length 22.5" in a medium','Machine wash cold, lay flat to dry'],'100% merino wool jersey',
   ['dance','hang','friend'],'lightweight all-merino jersey, relaxed and airy, black',
   'The airiest of the Unbound tanks. Pure merino jersey with no stretch fibre, cut to hang away from the body.'),
 (414,'Woolly Clothing Co.','https://www.woolly.clothing/products/w-ul-tank','M5','Racerback Tank',78,
   'A simple, classic racerback that is comfortable enough for home and technical enough for the trail: low-bulk athletic fit, moisture-wicking and odour-resistant, in ultra-soft Australian merino with a touch of elastane.',
   ['95% Australian merino, 5% elastane','175 gsm, 17.5 micron','Low-bulk athletic fit','Racerback','Responsible Wool Standard certified','Sizes XS to XXL'],'95% Australian merino, 5% elastane',
   ['dance','outdoors','hang'],'stretch merino, racerback frees the shoulders, athletic fit, black',
   'A strong dance pick: elastane keeps the shape when damp, and the racerback frees the shoulders.'),
 (415,'Woolly Clothing Co.','https://www.woolly.clothing/products/w-tank-crew','M4','Crew Tank',78,
   'A versatile companion that transitions from home to trail. Premium Australian merino with natural temperature regulation and freedom of movement, in an everyday 175 gsm weight with ultra-soft 17.5 micron fibres.',
   ['95% Australian merino, 5% elastane','175 gsm, 17.5 micron','Regular straps, scooped crew neckline','Responsible Wool Standard certified','Sizes XS to XXL'],'95% Australian merino, 5% elastane',
   ['dance','hang','friend'],'stretch merino, everyday weight, classic tank cut, black',
   'The same cloth as the racerback with regular straps and a flattering neckline, per its reviews.'),
 (416,'Icebreaker','https://na.icebreaker.com/en-us/womens-underwear/merino-150-siren-tank/103213.html','M13',"Merino 150 Siren Tank",75,
   'A soft, stretchy tank with a sleek, feminine design for everyday comfort, in durable corespun merino wool blend fabric. Sold as a base layer, worn on its own constantly; Icebreaker\'s most reviewed tank.',
   ['83% merino wool, 12% nylon, 5% elastane','150 gsm, 18.9 micron','Slim fit, close to the body','Corespun merino for durability','Sizes XS to XL'],'83% merino wool, 12% nylon, 5% elastane',
   ['dance','hang','outdoors'],'light corespun merino with stretch, slim, wicks and dries fast, black',
   'Icebreaker\'s most reviewed tank, light and stretchy. Filed under base layers on their site but worn solo all the time.'),
 (417,'Icebreaker','https://na.icebreaker.com/en-us/products/merino-blend-125-cool-lite-sphere-tank-ib0a56zq001','M14',"Merino Blend 125 Cool-Lite Sphere III Tank",80,
   'Soft, comfortable and versatile for warm-weather activity. Lightweight Cool-Lite merino and Tencel jersey with offset shoulder seams and a drop-tail hem.',
   ['60% Tencel lyocell, 40% merino wool','Cool-Lite jersey, the lightest weight Icebreaker makes','Regular fit, drop-tail hem','Offset shoulder seams','Sizes XS to XL'],'60% Tencel lyocell, 40% merino wool',
   ['dance','hang','outdoors'],'coolest fabric of the set, merino and Tencel, regular fit, black',
   'The coolest fabric here for a hot dance floor: merino blended with Tencel, which adds drape and dries even faster.'),
 (418,'Ridge Merino','https://ridgemerino.com/products/womens-journey-merino-wool-tank-top','M6',"Women's Journey Merino Wool Tank Top",45,
   'A versatile staple made from the same soft, breathable merino fabric as Ridge\'s bestselling Journey Tee. Nylon corespun merino for durability; naturally wicks sweat, dries quickly, resists odour and has built-in sun protection.',
   ['87% merino wool, 13% nylon corespun','150 gsm','Relaxed fit','UPF sun protection','Sizes XS to XL'],'87% merino wool, 13% nylon',
   ['dance','outdoors','hang'],'light corespun merino, relaxed, tough for the price, black',
   'The value pick. The nylon core makes it more durable than most merino at this weight, for $45.'),
 (419,'Ibex','https://ibex.com/products/womens-goat-tank','M8',"Women's GOAT Tank",75,
   'Ibex\'s favourite merino tank, now stronger and softer. Naturally moisture-wicking and odour-resistant, breathable for layering, with low-profile saddle stitching, offset shoulder seams and a curved hem made for tucking.',
   ['89% merino wool, 11% nylon','150 gsm','Relaxed fit','Curved hem','Black in S to XXL'],'89% merino wool, 11% nylon',
   ['dance','hang','outdoors'],'light merino-nylon, relaxed, curved hem tucks in, black',
   'A relaxed, tuckable merino tank from a long-running Vermont wool brand. Black runs S to XXL.'),
 (420,'Mons Royale','https://www.monsroyale.com/products/folo-merino-tank-black-womens','M9','Folo Merino Tank',74.95,
   'First on, last off. With a slim fit, scoop neck and straight hem, this merino tank is an essential all year. Ultralight and breathable, it regulates body temperature in all conditions.',
   ['83% merino wool, 13% nylon, 4% elastane','140 gsm, the lightest of the set','Slim fit, scoop neck, straight hem','Sizes XS to XL'],'83% merino wool, 13% nylon, 4% elastane',
   ['dance','outdoors','hang'],'lightest merino here, stretch, slim scoop neck, black',
   'The lightest tank of the ten, from a New Zealand bike-and-ski brand. Slim, stretchy and built for sweating in.'),
 (421,'Minus33','https://www.minus33.com/products/lafayette-womens-lightweight-wool-tank-top','M11',"Lafayette Lightweight Wool Tank Top",59.99,
   'When it is so hot all you want is the beach, this is the tank. Lightweight and breathable 100% merino jersey that keeps you cool and dry through the day.',
   ['100% merino wool','170 gsm lightweight jersey, 17.5 micron','Straight cut','Machine washable','Sizes XS to XL'],'100% merino wool',
   ['dance','hang','outdoors'],'all-merino lightweight jersey, plain and honest, black',
   'The plainest and one of the cheapest all-wool options, from a New Hampshire base-layer maker.'),
]
extras=json.load(open('build/extras.json'))
extras=[e for e in extras if e['id']<412]
for iid,brand,url,key,name,price,desc,details,fabric,occ,why,note in T:
    img=f'images/full/{iid:03d}.jpg'
    # try for a black-colourway photo from the product feed
    got=False
    try:
        d=json.loads(urllib.request.urlopen(urllib.request.Request(url.split('?')[0]+'.js',headers=H),timeout=30,context=ctx).read())
        cand=None
        for v in d.get('variants',[]):
            if re.search(r'black',v.get('title',''),re.I) and v.get('featured_image'): cand=v['featured_image']['src']; break
        if not cand:
            for src in d.get('images',[]):
                if re.search(r'black|blk|_bk',src,re.I): cand=src; break
        if cand:
            u=('https:'+cand if cand.startswith('//') else cand).split('?')[0]+'?width=1000'
            im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30,context=ctx).read())).convert('RGB'); im.thumbnail((900,900)); im.save(img,'JPEG',quality=82,optimize=True); got=True
    except Exception as e: pass
    if not got: shutil.copy(f'build/merino/{key}.jpg', img)
    extras.append(dict(id=iid, brand=brand, retailer=brand, name=name, category='Tops & Tees', color='Black', occasions=occ, why=why, price=price,
        colorDetail='Black', categoryDetail='Merino tank', url=url, img=img, hi=True, desc=desc, details=details, fabric=fabric, note=note))
    print(iid, brand, name, '| black photo from feed:', got)
json.dump(extras, open('build/extras.json','w'), indent=1, ensure_ascii=False)
print(len(extras), 'extras total')
