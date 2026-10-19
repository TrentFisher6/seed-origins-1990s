"""Do the non-MinghuaQu parts carry meaning? Printable-ASCII runs (both nibble alignments, also 7-bit masked), BCD/decimal-only
stretches, and byte-reversed ASCII, compared with a random-filler control at the same positions."""
import json, random, re
MQ = b'MinghuaQu'.hex()
S = sorted(set([s for l, s in json.load(open('data/all_seeds.json')) if MQ in s] + ['24b7b137c8a14d696e6768756151756fd0da2e5c']))
def parts(s):
    k = s.find(MQ); return [s[:k], s[k+18:]]
def runs(h):
    out = []
    for off in (0, 1):
        x = h[off:]; b = bytes.fromhex(x[:len(x)//2*2]) if len(x) >= 2 else b''
        for bb in (b, b[::-1]):
            for m in re.finditer(rb'[A-Za-z0-9 .,_\-]{3,}', bb): out.append(m.group().decode())
    return out
def stats(seeds):
    nrun = sum(len(runs(p)) for s in seeds for p in parts(s))
    longest = max((len(r) for s in seeds for p in parts(s) for r in runs(p)), default=0)
    dec = sum(len(m.group()) for s in seeds for p in parts(s) for m in re.finditer(r'[0-9]{6,}', p))
    return nrun, longest, dec
real = stats(S)
rng = random.Random(3); null = []
for t in range(300):
    R = []
    for s in S:
        k = s.find(MQ); f = ''.join(rng.choice('0123456789abcdef') for _ in range(22)); R.append(f[:k] + MQ + f[k:])
    null.append(stats(R))
print('real: #ASCII runs>=3, longest run, decimal-only digits in runs>=6 :', real)
for i, name in enumerate(('#runs', 'longest', 'decimal digits')):
    v = sorted(n[i] for n in null); print(f'  null {name}: median {v[150]}, 95% {v[284]}, max {v[-1]}; P(null>=real) = {sum(x >= real[i] for x in v)/300:.2f}')
print('real ASCII runs:', sorted({r for s in S for p in parts(s) for r in runs(p) if len(r) >= 4}))
