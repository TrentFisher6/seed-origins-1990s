"""Null control for the reuse graph: replace every MQ seed's filler with random hex (keeping its k), count edges under chronology.py's rules."""
import json, random, itertools, sys
sys.path.insert(0, 'scripts')
MQ = b'MinghuaQu'.hex()
S = [s for l, s in json.load(open('data/all_seeds.json')) if MQ in s] + ['24b7b137c8a14d696e6768756151756fd0da2e5c']
S = sorted(set(S))
def F(s): k = s.find(MQ); return k, s[:k] + s[k+18:]
def edge(a, b):
    ka, Fa = F(a); kb, Fb = F(b)
    if ka == kb and sum(x == y for x, y in zip(a, b)) >= 24: return 1
    if ka != kb and Fa[2:-3] == Fb[2:-3]: return 1
    return 0
real = sum(edge(a, b) for a, b in itertools.combinations(S, 2))
rng = random.Random(7); counts = []
for trial in range(200):
    R = []
    for s in S:
        k = s.find(MQ); f = ''.join(rng.choice('0123456789abcdef') for _ in range(22)); R.append(f[:k] + MQ + f[k:])
    counts.append(sum(edge(a, b) for a, b in itertools.combinations(R, 2)))
print('distinct seeds', len(S), 'real edges', real, '| null: mean', sum(counts) / len(counts), 'max', max(counts),
      'P(null>=1)', sum(c >= 1 for c in counts) / len(counts))
# strongest-evidence per edge: number of equal non-MQ nibbles
