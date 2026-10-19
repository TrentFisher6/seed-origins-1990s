"""FreeLIP zrstarts(seed) for small seeds; test MQ fillers under: (a) nibble = limb&15 stream, (b) byte = limb&255 stream,
(c) zrandomb(2^160)-style 160-bit candidates (8 limbs top-first mod 2^160) with insert/overwrite models. Usage: lip_small.py s0 s1 nout"""
import json, sys
M = 2**107 - 1; A = pow(3, 121, M)
MQ = b'MinghuaQu'.hex()
L = 10
win = {}
for l, s in json.load(open('data/all_seeds.json')) + json.load(open('data/planted_lip.json')):
    k = s.find(MQ)
    if k < 0: continue
    for part in (s[:k], s[k+18:], s[:k] + s[k+18:]):
        for j in range(len(part) - L + 1): win.setdefault(part[j:j+L], l)
s0, s1, nout = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
for sd in range(s0, s1):
    st = sd; limbs = []
    for _ in range(nout):
        st = st * A % M; limbs.append(st & 0x3ffffff)
    nib = ''.join('%x' % (v & 15) for v in limbs)
    byt = ''.join('%02x' % (v & 255) for v in limbs)
    cands = [nib, byt]
    for j in range(0, nout - 8):
        x = 0
        for v in limbs[j:j+8]: x = x << 26 | v
        cands.append('%040x' % (x % 2**160))
    for ci, c in enumerate(cands):
        for j in range(len(c) - L + 1):
            if c[j:j+L] in win: print('HIT seed', sd, 'cand', ci, 'pos', j, c[j:j+L], win[c[j:j+L]], flush=True)
print('done', s0, s1, file=sys.stderr)
