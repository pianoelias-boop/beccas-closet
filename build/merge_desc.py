import json, re, ssl, urllib.request, html, os, time, concurrent.futures as cf
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36','Accept':'text/html,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30,context=ctx).read().decode('utf-8','ignore')
items=json.load(open('build/items_raw.json'))
raw=json.load(open('build/desc_raw.json')); bdesc=json.load(open('build/browser_desc.json')); anthro=json.load(open('build/anthro.json'))

# ---- extra specs: Boden fabric & care, A&F fiber content (cached) ----
XP='build/extra_specs.json'
extra=json.load(open(XP)) if os.path.exists(XP) else {}
def fetch_extra(it):
    k=str(it['id'])
    if k in extra: return k, extra[k]
    for attempt in range(3):
        try:
            page=get(it['url'])
            if it['retailer']=='Boden':
                i=page.find('Fabric &amp; care')
                if i<0: return k, None
                seg=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','\n',page[i:i+3000])))
                seg=seg.split('{')[0].replace('Fabric & care','').strip()
                # "Composition Main: 50% cotton, 50% TENCEL ™ Modal Fabric Detachable self fabric belt Care Machine washable"
                comp=re.search(r'Composition\s*(.*?)\s*(?:Fabric\s|Care\s|$)', seg); care=re.search(r'Care\s*(.*)$', seg); fab=re.search(r'Fabric\s+(?!&)(.*?)\s*(?:Care\s|$)', seg)
                # also "Fit & size" bullets
                j=page.find('Fit &amp; size'); fit=None
                if j>=0:
                    fseg=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','\n',page[j:j+2500]))).split('{')[0].replace('Fit & size','').strip()
                    fit=fseg[:220]
                return k, {'composition':comp.group(1).strip() if comp else None,'fabric':fab.group(1).strip() if fab else None,'care':care.group(1).strip()[:80] if care else None,'fit':fit}
            else:  # A&F
                m=re.search(r'"FiberContent":\{"values":\[(.*?)\]', page)
                vals=re.findall(r'"value":"([^"]+)"', m.group(1)) if m else []
                return k, {'composition':'; '.join(v.title() for v in vals if not re.match(r'(ELASTIC|PAD|LABEL|THREAD|EMBROIDERY|TRIM)', v))[:160] or None}
        except Exception as e:
            time.sleep(1.5)
    return k, None
todo=[it for it in items if it['retailer'] in ('Boden','Abercrombie & Fitch')]
with cf.ThreadPoolExecutor(6) as ex:
    for k,v in ex.map(fetch_extra, todo):
        extra[k]=v
json.dump(extra,open(XP,'w'),indent=1,ensure_ascii=False)
print('extra specs:', sum(1 for v in extra.values() if v), '/', len(todo))

# ---- normalisation ----
FABRIC_WORDS=r'cotton|linen|wool|cashmere|silk|viscose|rayon|lyocell|tencel|modal|polyester|nylon|elastane|spandex|lycra|polyamide|acrylic|alpaca|mohair|hemp|ramie|cupro|leather|denim|jersey|poplin|chambray|corduroy|velvet|satin|chiffon|voile|twill|gauze|crepe|merino|lambswool'
JUNK=re.compile(r'^(imported|select stores|online only|item [a-z0-9]+|###|details|dimensions|size guide|style no\.|model|shipping|returns|share|approximate|us size|xs|s|m|l|xl)\b', re.I)
SPEC=re.compile(r'(\d{1,3}\s?%|^(fabric|material|composition|care|fit|made in|machine wash|hand wash|dry clean|inseam|rise|length|leg opening|falls|measures|lined|unlined|pockets?|zip|button|pull-?on|elastic|stretch|sheer|relaxed|slim|regular|oversized|cropped|high[- ]rise|mid[- ]rise|wide[- ]leg|a-line|midi|maxi|mini)\b)', re.I)
def clean_line(s):
    s=re.sub(r'\s+',' ',s).strip(' -•·*:').strip()
    s=s.replace('â¦','…').replace('â','’')
    return s
def split_lines(text):
    out=[]
    for ln in re.split(r'\n+|(?<=[.!?])\s+(?=[A-Z])', text or ''):
        ln=clean_line(ln)
        if ln: out.append(ln)
    return out
def build(it):
    k=str(it['id']); prose=[]; specs=[]
    if k in anthro:
        pd=anthro[k].get('pd') or ''
        lines=split_lines(pd)
        for ln in lines:
            (specs if len(ln)<70 or '%' in ln else prose).append(ln)
        if anthro[k].get('sf'): specs.append(anthro[k]['sf'])
    elif k in bdesc:
        prose=split_lines(bdesc[k]['desc']); specs=[clean_line(x) for x in bdesc[k].get('lis',[])]
    else:
        r=raw.get(k) or {}
        for ln in split_lines(r.get('desc')):
            (specs if (len(ln)<70 and SPEC.search(ln)) or re.search(r'\d{1,3}\s?%',ln) and len(ln)<120 else prose).append(ln)
        if it['retailer'] not in ('Abercrombie & Fitch',):
            for f in r.get('fabric') or []:
                f=clean_line(f)
                if 8<len(f)<110 and '"' not in f and '{' not in f: specs.append(f)
    x=extra.get(k)
    if x:
        if x.get('composition'): specs.insert(0, x['composition'])
        if x.get('fabric'): specs.append(x['fabric'])
        if x.get('fit'): specs.append(x['fit'])
        if x.get('care'): specs.append(x['care'])
    # prose: drop brand-history paragraphs and junk; cap length
    BLURB=re.compile(r'founded|was born|started (his|her) line|since \d{4}|in \d{4},|launched by|the brand|our brand|shipping container|collection brimming|lifestyle brand|only-at-anthro|his bread and butter', re.I)
    kept=[p for p in prose if not JUNK.match(p) and not BLURB.search(p)]
    prose=kept or prose[:1]
    desc=' '.join(prose)
    if len(desc)>720:
        cut=desc[:720]; desc=cut[:cut.rfind('. ')+1] if '. ' in cut[300:] else cut+'…'
    # specs: dedupe, drop junk, cap
    seen=set(); det=[]
    for s in specs:
        s=clean_line(s).rstrip('.')
        low=s.lower()
        if not s or JUNK.match(s) or len(s)>110 or low in seen or 'size chart' in low or 'measurements' in low: continue
        if low.startswith('style no') or low==it['brand'].lower() or low in ('imported','hand wash','machine wash','dry clean','select stores','online only'): continue
        if BLURB.search(s) or s.endswith('?'): continue
        if re.match(r'^(size|us size|xs|small|medium|large|x-large)\b', low): continue
        seen.add(low); det.append(s)
    det=det[:8]
    pct=[d for d in det if re.search(r'\d{1,3}\s?%', d)]
    fab=(min(pct, key=len) if pct else None) or next((d for d in det if len(d)<80 and re.search(r'(?i)\b('+FABRIC_WORDS+r')\b', d) and not re.search(r'(?i)pocket|wash|zip|button', d)), None)
    if fab:
        fab=re.split(r'\s+(?:Trims?|Lining|Bodice lining|Contrast|Pocket bag|Rib|Embroidery)\s*:', fab)[0].strip()
        fab=re.sub(r'^(?:Main|Body|Shell|Fabric|Composition|Material)\s*:\s*', '', fab, flags=re.I)
        fab=re.sub(r'^Machine wash \d+ºC\.\s*', '', fab)
        if len(fab)>90: fab=fab[:90].rsplit(' ',1)[0]+'…'
    if fab:
        det=[d for d in det if d!=fab and not re.search(r'\d{1,3}\s?%', d) or (re.search(r'\d{1,3}\s?%', d) and d!=fab and fab not in d and not d.startswith(('Main:','Machine wash')))]
        det=[re.sub(r'^(?:Main|Body|Shell)\s*:\s*','',d) for d in det]
    return {'desc': desc or None, 'details': det, 'fabric': fab}
final={str(it['id']): build(it) for it in items}
json.dump(final, open('build/desc_final.json','w'), indent=1, ensure_ascii=False)
import collections
by=collections.defaultdict(lambda:[0,0,0])
for it in items:
    f=final[str(it['id'])]; b=by[it['retailer']]; b[2]+=1
    if f['desc']: b[0]+=1
    if f['fabric']: b[1]+=1
for k,(d,f,t) in sorted(by.items()): print(f'{k:22s} desc {d:3d}/{t:<3d} fabric {f:3d}/{t}')
