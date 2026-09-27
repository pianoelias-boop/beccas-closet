"""Local preview server with curator mode. Run from anywhere:  python3 build/dev_server.py [port]

Serves the site like `python3 -m http.server` and adds a small API, on 127.0.0.1 only, that the page uses
when it finds it (the curator panel in each item's detail view):

  GET  /__curate/ping                      -> {"ok": true}
  POST /__curate  {"id": 452, "priority": "dance-jumpsuit", "on": true}    put a piece in / take it out of a priority
  POST /__curate  {"id": 165, "occasion": "dance", "on": true}             add / remove an occasion tag

Priority changes rewrite priorities.js (pin and drop lists). Occasion changes go to build/extras.json for
pieces added by CSV, or to build/occ/out_zcurated.json (read last by make_data.py) for the original
catalog, and then data.js is rebuilt. Nothing is committed or pushed: review on localhost, then publish.
The public site never sees this API; GitHub Pages serves static files only.
"""
import json, os, re, subprocess, sys, glob
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'build'))
from closet_config import load, occasion_keys

PRI_PATH = 'priorities.js'
CURATED = 'build/occ/out_zcurated.json'


def read_priorities():
    txt = open(PRI_PATH, encoding='utf-8').read()
    m = re.search(r'(?m)^window\.CLOSET_PRIORITIES\s*=', txt)   # the assignment line, not the mention in the header comment
    return txt[:m.start()], json.loads(txt[m.end():].strip().rstrip(';'))


def write_priorities(head, pris):
    out = json.dumps(pris, indent=1, ensure_ascii=False)
    out = re.sub(r'\[\s*((?:"(?:[^"\\]|\\.)*"|-?\d+)(?:,\s*(?:"(?:[^"\\]|\\.)*"|-?\d+))*)\s*\]', lambda m: '[' + re.sub(r',\s*', ', ', m.group(1)) + ']', out)   # short lists on one line
    open(PRI_PATH, 'w', encoding='utf-8').write(head + 'window.CLOSET_PRIORITIES = ' + out + ';\n')


def catalogue():
    return {i['id']: i for i in json.loads(open('data.js', encoding='utf-8').read().split('= ', 1)[1].rstrip(';\n'))}


def set_priority(iid, key, on, fits_by_rule):
    """on: the piece should be in the priority. fits_by_rule: the page's verdict from the rule alone (no pin/drop)."""
    head, pris = read_priorities()
    p = next((x for x in pris if x['key'] == key), None)
    if not p: raise ValueError(f'no priority {key}')
    m = p.setdefault('match', {})
    pin, drop = set(m.get('pin', [])), set(m.get('drop', []))
    pin.discard(iid); drop.discard(iid)
    if on and not fits_by_rule: pin.add(iid)
    if not on and fits_by_rule: drop.add(iid)
    for k, s in (('pin', pin), ('drop', drop)):
        if s: m[k] = sorted(s)
        else: m.pop(k, None)
    write_priorities(head, pris)
    return pris


def set_occasion(iid, occ, on):
    if occ not in occasion_keys(load()): raise ValueError(f'unknown occasion {occ}')
    if iid >= 5000: raise ValueError('weekly ideas keep the tags the round gave them')
    extras = json.load(open('build/extras.json', encoding='utf-8'))
    ex = next((e for e in extras if e['id'] == iid), None)
    if ex:
        tags = [t for t in ex['occasions'] if t != occ] + ([occ] if on else [])
        ex['occasions'] = tags
        json.dump(extras, open('build/extras.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    else:
        item = catalogue().get(iid)
        if not item: raise ValueError(f'no piece {iid}')
        cur = json.load(open(CURATED, encoding='utf-8')) if os.path.exists(CURATED) else {}
        tags = [t for t in item['occasions'] if t != occ] + ([occ] if on else [])
        cur[str(iid)] = {'tags': tags, 'why': item.get('why')}
        os.makedirs(os.path.dirname(CURATED), exist_ok=True)
        json.dump(cur, open(CURATED, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, 'build/make_data.py'], check=True, stdout=subprocess.DEVNULL)
    return catalogue()[iid]['occasions']


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')   # always the latest files while curating
        super().end_headers()

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith('/__curate/ping'): return self._json({'ok': True})
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith('/__curate'): return self._json({'ok': False, 'error': 'not found'}, 404)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
            iid = int(body['id']); on = bool(body.get('on'))
            if 'priority' in body:
                pris = set_priority(iid, str(body['priority']), on, bool(body.get('fitsByRule')))
                print(f'curate: {iid} {"into" if on else "out of"} {body["priority"]}')
                return self._json({'ok': True, 'priorities': pris})
            if 'occasion' in body:
                tags = set_occasion(iid, str(body['occasion']), on)
                print(f'curate: {iid} occasion {body["occasion"]} {"on" if on else "off"} -> {tags}')
                return self._json({'ok': True, 'occasions': tags})
            raise ValueError('say priority or occasion')
        except Exception as e:
            return self._json({'ok': False, 'error': str(e)}, 400)

    def log_message(self, fmt, *args):
        if '/__curate' in (args[0] if args else ''): super().log_message(fmt, *args)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
    print(f'Closet preview with curator mode: http://localhost:{port}  (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
