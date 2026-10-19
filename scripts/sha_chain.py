"""Are MQ fillers the leading hex digits of SHA-1(z+d) for some other published seed z and |d| <= D? (aligned test: digits 2..9)"""
import json, hashlib, sys
MQ = b'MinghuaQu'.hex()
S = [(l, s) for l, s in json.load(open('data/all_seeds.json'))]
key = {}
for l, s in S:
    k = s.find(MQ)
    if k >= 0:
        F = s[:k] + s[k+18:]
        key.setdefault(F[2:10], l)          # insert model, first byte may be edited
z0 = 0x1234567890abcdef1234567890abcdef12345678                   # planted control
key.setdefault(hashlib.sha1((z0 + 777).to_bytes(20, 'big')).hexdigest()[2:10], 'PLANT')
part, nparts, D = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
bases = [s for _, s in S] + ['%040x' % z0]
for idx, s in enumerate(bases):
    if idx % nparts != part: continue
    z = int(s, 16)
    for d in range(-D, D + 1):
        h = hashlib.sha1(((z + d) % 2**160).to_bytes(20, 'big')).hexdigest()
        if h[2:10] in key: print('HIT', s, d, h, key[h[2:10]], flush=True)
print('done', part, file=sys.stderr)
