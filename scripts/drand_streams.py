"""Unseeded drand48 family (state 0x1234ABCD330E) and srand48(s) for small s: lrand48 outputs, all byte shifts and nibble shifts;
search DSA KSEED/SEED, B-163 (5-byte pieces) and MQ filler windows (10 nibbles)."""
import json, sys
A, C, M = 0x5DEECE66D, 0xB, (1 << 48) - 1
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
starts = [('unseeded', 0x1234ABCD330E)] + [(f'srand48({s})', (s << 16) | 0x330E) for s in range(int(sys.argv[1]))]
N = int(sys.argv[2])
# planted: srand48(5), (lrand48()>>9)&0xff bytes from output 100
x = (5 << 16) | 0x330E; pl = []
for i in range(130):
    x = (A * x + C) & M
    if i >= 100: pl.append(((x >> 17) >> 9) & 0xff)
win[bytes(pl).hex()[:10]] = 'PLANT'
for name, x0 in starts:
    x = x0; outs = []
    for _ in range(N):
        x = (A * x + C) & M; outs.append(x >> 17)
    for sh in range(24):
        st = bytes((v >> sh) & 0xff for v in outs).hex()
        for j in range(0, len(st) - L + 1):
            if st[j:j+L] in win: print('HIT', name, 'byteshift', sh, j, st[j:j+L], win[st[j:j+L]], flush=True)
    for sh in range(28):
        st = ''.join('%x' % ((v >> sh) & 15) for v in outs)
        for j in range(len(st) - L + 1):
            if st[j:j+L] in win: print('HIT', name, 'nibshift', sh, j, st[j:j+L], win[st[j:j+L]], flush=True)
print('done')
