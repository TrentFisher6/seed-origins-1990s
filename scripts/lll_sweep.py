"""LLL sweep: is a bit-string a run of consecutive top-w-bit lrand48 outputs (any bit alignment)? w in 4,8,12,16,24,31(lrand48 words, top bit 0),32(mrand48)."""
import json, sys, datetime
sys.path.insert(0, 'scripts')
from lcg_lll import recover, find_srand
MQ = b'MinghuaQu'.hex()
targets = [('DSA1994_SEED', 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd'),
           ('DSA186-1_SEED', 'd5014e4b60ef2ba8b6211b4062ba3224e0427dd3'),
           ('DSA_XSEED', 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6'),
           ('DSA_KSEED', '687a66d90648f993867e121f4ddf9ddb01205584'),
           ('B-163', '85e25bfe5c86226cdb12016f7553f9d0e693a268'),
           ('CONTROL_P256', 'c49d360886e704936a6678e1139d26b7819f7e90')]
for l, s in json.load(open('data/all_seeds.json')):
    if MQ in s:
        k = s.find(MQ); targets.append((l + ':F', s[:k] + s[k+18:]))
for lab, hx in targets:
    bits = bin(int(hx, 16))[2:].zfill(len(hx) * 4)
    for w, word in ((4, 4), (8, 8), (12, 12), (16, 16), (24, 24), (31, 32), (32, 32)):
        for off in range(word):
            known = {}
            j = 0
            while off + (j + 1) * word <= len(bits):
                chunk = bits[off + j*word: off + (j+1)*word]
                if word == 32 and w == 31:
                    if chunk[0] != '0': known = None; break
                    chunk = chunk[1:]
                known[j] = int(chunk, 2); j += 1
            if not known or len(known) * w < 56: continue
            for x in recover(known, w):
                r = find_srand(x, 1 << 22)
                ts = datetime.datetime.fromtimestamp(r[1], datetime.UTC) if r else None
                print('HIT', lab, 'w', w, 'off', off, hex(x), r, ts, flush=True)
print('done')
