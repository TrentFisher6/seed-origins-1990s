"""MQ fillers vs BSD random() (init=1) low-byte / low-nibble streams for all seed classes mod 512, long streams."""
import sys, json
sys.path.insert(0, 'scripts')
from bsd_random import bsd_random
MQ = b'MinghuaQu'.hex(); L = 10
win = {}
for l, s in json.load(open('data/all_seeds.json')):
    k = s.find(MQ)
    if k < 0: continue
    for part in (s[:k], s[k+18:], s[:k] + s[k+18:]):
        for j in range(len(part) - L + 1): win.setdefault(part[j:j+L], l)
# planted: class 77, byte stream from output 5000, MQ inserted at 7
o = bsd_random(77, 6000); h = bytes(v & 0xff for v in o[5000:5020]).hex(); win.setdefault((h[:7] + MQ + h[7:])[:7] + h[7:10], 'PLANT')
win.setdefault(h[2:12], 'PLANT2')
N = int(sys.argv[1])
for c in range(512):
    o = bsd_random(c, N, 1)
    for nm, st in (('byte', bytes(v & 0xff for v in o).hex()), ('nib', ''.join('%x' % (v & 15) for v in o))):
        if nm == 'nib' and c >= 32: continue
        for j in range(len(st) - L + 1):
            w = st[j:j+L]
            if w in win: print('HIT', c, nm, j, w, win[w], flush=True)
print('done')
