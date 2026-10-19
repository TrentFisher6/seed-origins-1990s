"""Overwrite model: published seed s = h with hex("MinghuaQu") written over positions k..k+17, h = SHA-1(z+d) for a published seed z (incl. s itself),
|d|<=D. Aligned key: 8 known nibbles of s at fixed positions (inside the longer side, avoiding the possibly edited first 2 / last 1 nibbles)."""
import json, hashlib, sys
MQ = b'MinghuaQu'.hex()
S = [s for _, s in json.load(open('data/all_seeds.json'))]
keys = {}   # (pos) -> {8-nibble: seed}
def add(s, lab):
    k = s.find(MQ)
    if k < 0: return
    pos = 2 if k >= 10 else k + 18 + (1 if 40 - (k + 18) - 1 >= 9 else 0)
    if pos + 8 > 39 and pos >= k + 18: pos = 31
    keys.setdefault(pos, {})[s[pos:pos+8]] = lab
for s in set(S): add(s, s)
# planted: h = sha1(z0 + 4242), MQ over positions 13..30
z0 = int(S[5], 16); h = hashlib.sha1((z0 + 4242).to_bytes(20, 'big')).hexdigest(); planted = h[:13] + MQ + h[31:]
add(planted, 'PLANT')
part, nparts, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
bases = sorted(set(S))
for i, s in enumerate(bases):
    if i % nparts != part: continue
    z = int(s, 16)
    for d in range(-D, D + 1):
        h = hashlib.sha1(((z + d) % 2**160).to_bytes(20, 'big')).hexdigest()
        for pos, tab in keys.items():
            if h[pos:pos+8] in tab: print('HIT base', s, 'd', d, 'pos', pos, h, '->', tab[h[pos:pos+8]], flush=True)
print('done', part, file=sys.stderr)
