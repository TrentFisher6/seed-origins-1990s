"""Emit target runs for lcgbf. Usage: mk_targets.py w out.txt [planted]"""
import json, sys
MQ = b'MinghuaQu'.hex()
w = int(sys.argv[1]); out = open(sys.argv[2], 'w')
seeds = [tuple(x) for x in json.load(open('data/all_seeds.json'))]
if len(sys.argv) > 3: seeds += [tuple(x) for x in json.load(open(sys.argv[3]))]
def emit(lab, hexrun):
    if w == 4: vals = [int(ch, 16) for ch in hexrun]
    else: vals = [int(hexrun[i:i+2], 16) for i in range(0, len(hexrun) - 1, 2)]
    if len(vals) * w >= 40: out.write(lab + ' ' + ' '.join(map(str, vals)) + '\n')
for lab, s in seeds:
    k = s.find(MQ)
    if k < 0: continue
    F = s[:k] + s[k+18:]
    emit(lab + ':ins', F[1:-1] if w == 4 else F[2:-2])        # insert model, ends trimmed
    if w == 8 and k % 2 == 1: emit(lab + ':ins1', F[1:-1])     # odd alignment for bytes
    pre, suf = s[:k], s[k+18:]
    for name, r in (('pre', pre[1:]), ('suf', suf[:-1])):     # overwrite model runs
        emit(lab + ':' + name, r if w == 4 or len(r) % 2 == 0 else r[:-1])
