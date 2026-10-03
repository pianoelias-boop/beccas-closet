"""Exit 0 if the pending shortlist is usable for a round, 1 if it is too thin (the week should be skipped).

A shortlist from fewer than 5 brands or with fewer than 30 pieces means the brand feeds mostly failed, as in
October 2026 when Shopify refused GitHub's machines. Both round jobs call this before publishing anything.
"""
import json, os, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pending', 'shortlist.json')
s = json.load(open(p)) if os.path.exists(p) else []
brands = len({x['brand'] for x in s}); ok = len(s) >= 30 and brands >= 5
print(f'shortlist: {len(s)} pieces from {brands} brands' + ('' if ok else ', too thin, skipping this week'), file=sys.stderr)
sys.exit(0 if ok else 1)
