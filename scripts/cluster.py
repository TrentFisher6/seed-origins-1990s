import json, collections
MQ = b'MinghuaQu'.hex()
C = json.load(open('data/openssl_curves.json'))
seeds = []  # (label, seedhex)
for k, v in C.items():
    if v['seed'] and not k.startswith('wap'): seeds.append((k, v['seed']))
cc = json.load(open('data/agent/certicom.json'))['curves']
for k, v in cc.items():
    for f in ('seedE', 'seedP', 'seedQ'):
        if v.get(f): seeds.append((f'{k}.{f}', v[f].lower()))
json.dump(seeds, open('data/all_seeds.json', 'w'), indent=0)
groups = collections.defaultdict(list)
for lab, s in seeds:
    i = s.find(MQ)
    F = s[:i] + s[i+18:] if i >= 0 else None
    groups[(s[:-1])].append((lab, s, i))
print('n seeds', len(seeds), 'with MQ', sum(MQ in s for _, s in seeds))
for key, g in groups.items():
    if len(g) > 1: print('SAME-BUT-LAST:', [(l, s[-1]) for l, s, i in g], key)
# looser: same filler minus first byte & last nibble
g2 = collections.defaultdict(list)
for lab, s in seeds:
    i = s.find(MQ)
    if i < 0: continue
    F = s[:i] + s[i+18:]
    g2[F[2:-1]].append((lab, i, s))
for key, g in g2.items():
    if len(g) > 1 and len({x[2][:-1] for x in g}) > 1: print('SAME-MID:', key, g)
for lab, s in seeds:
    i = s.find(MQ)
    print(f"{lab:22s} k={i:3d} {s}")
