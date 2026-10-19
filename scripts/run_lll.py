"""Test every MQ seed: are the filler nibbles/bytes consecutive lrand48 top-window outputs? (LLL)"""
import json, sys, datetime
sys.path.insert(0, 'scripts')
from lcg_lll import recover, find_srand
MQ = b'MinghuaQu'.hex()
seeds = [tuple(x) for x in json.load(open('data/all_seeds.json'))]
def models(s):
    k = s.find(MQ); F = s[:k] + s[k+18:]
    out = {}
    # insert model: F nibble j is output j (nibble) / byte j
    out['ins'] = {j: F[j] for j in range(22)}
    # overwrite model: seed nibble positions outside MQ
    out['ovw'] = {j: s[j] for j in range(40) if not (k <= j < k + 18)}
    # NIST-style: MQ seed entirely random except MQ? (same as ovw)
    return out
hits = 0
for lab, s in seeds:
    if MQ not in s: continue
    for mname, nib in models(s).items():
        for w in (4, 8):
            if w == 4:
                known = {j: int(v, 16) for j, v in nib.items()}
            else:
                known = {j // 2: int(nib[j] + nib[j+1], 16) for j in nib if j % 2 == 0 and j + 1 in nib}
            # drop first and last known output (end edits)
            ks = sorted(known)
            for trim in (0, 1):
                kk = {i: known[i] for i in ks[trim:len(ks)-trim]}
                if len(kk) * w < 60: continue
                c = recover(kk, w)
                if c:
                    hits += 1
                    for x in c:
                        r = find_srand(x, 1 << 20)
                        ts = datetime.datetime.utcfromtimestamp(r[1]) if r else None
                        print('HIT', lab, mname, w, trim, hex(x), r, ts)
print('done, hits', hits)
