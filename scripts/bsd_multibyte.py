"""Unseeded BSD random() stream, multi-byte-per-call extractions: 16-bit (low/high, BE/LE), 24-bit low BE/LE, 32-bit LE of 31-bit.
Search KSEED/SEED94/B-163 pieces and MQ filler windows."""
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
for n, t in {'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584', 'SEED94': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd',
             'B-163': '85e25bfe5c86226cdb12016f7553f9d0e693a268', 'XSEED': 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6'}.items():
    win[t[:10]] = n; win[t[30:]] = n
seeds = [int(x) for x in sys.argv[1].split(',')]
N = int(sys.argv[2])
for sd in seeds:
    o = bsd_random(sd, N)
    ex = {
     'lo16BE': b''.join((v & 0xffff).to_bytes(2, 'big') for v in o), 'lo16LE': b''.join((v & 0xffff).to_bytes(2, 'little') for v in o),
     'hi16BE': b''.join((v >> 15).to_bytes(2, 'big') for v in o), 'hi16LE': b''.join((v >> 15).to_bytes(2, 'little') for v in o),
     'lo24BE': b''.join((v & 0xffffff).to_bytes(3, 'big') for v in o), 'lo24LE': b''.join((v & 0xffffff).to_bytes(3, 'little') for v in o),
     'w32LE': b''.join(v.to_bytes(4, 'little') for v in o), 'w32BE': b''.join(v.to_bytes(4, 'big') for v in o),
    }
    for nm, b in ex.items():
        st = b.hex()
        for j in range(len(st) - L + 1):
            if st[j:j+L] in win: print('HIT', sd, nm, j, st[j:j+L], win[st[j:j+L]], flush=True)
print('done')
