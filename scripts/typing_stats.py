"""Are MQ-seed fillers uniform random hex, or human-typed? Compare against NIST/X9.62-prime seeds (lrand48) and SHA-1 control."""
import json, collections, hashlib, math, random
MQ = b'MinghuaQu'.hex()
seeds = [tuple(x) for x in json.load(open('data/all_seeds.json'))]
# dedupe: keep unique fillers by seed[1:-1] to avoid double counting near-copies
fills, seen = [], set()
for l, s in seeds:
    if MQ not in s: continue
    i = s.find(MQ); F = s[:i] + s[i+18:]
    key = F[2:-1]
    if key in seen: continue
    seen.add(key); fills.append((l, s[:i], s[i+18:]))
ctrl = [s for l, s in seeds if MQ not in s]
def stats(strings, name):
    cnt = collections.Counter(''.join(strings)); n = sum(cnt.values())
    chi = sum((cnt[c] - n/16)**2/(n/16) for c in '0123456789abcdef')
    rep = sum(a == b for s in strings for a, b in zip(s, s[1:])); pairs = sum(len(s)-1 for s in strings)
    digits = sum(cnt[c] for c in '0123456789')/n
    print(f"{name:28s} n={n:5d} chi2(15df)={chi:7.1f} adjacent-repeat={rep/pairs:.3f} (exp .0625) digit-frac={digits:.3f} (exp .625)")
    print('   counts', ''.join(f"{c}:{cnt[c]} " for c in '0123456789abcdef'))
stats([p + s for _, p, s in fills], 'MQ fillers (unique families)')
stats([p for _, p, s in fills], '  prefixes')
stats([s for _, p, s in fills], '  suffixes')
stats(ctrl, 'non-MQ seeds (NIST/X9.62 prime)')
random.seed(1)
stats([hashlib.sha1(str(i).encode()).hexdigest()[:22] for i in range(len(fills))], 'control: sha1 random')
print('chi2 15df: p=0.05 -> 25.0, p=0.001 -> 37.7')
