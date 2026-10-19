"""Seed-reuse graph across documents. Edge if two MQ seeds have MQ at the same k and >= 24 aligned equal nibbles, or the same filler F
(ignoring first byte / last 3 nibbles) with MQ moved. Prints connected components with document dates."""
import json, itertools
MQ = b'MinghuaQu'.hex()
DOC = {'cert': 'Certicom ECC Challenge (1997-11-06)', 'x962': 'ANSI X9.62 (1998/99)', 'secg': 'SEC 2 v1 (2000-09)'}
nodes = []
for l, s in json.load(open('data/all_seeds.json')):
    if MQ not in s: continue
    doc = 'cert' if l.startswith('ECC') else ('x962' if l.startswith('X9_62') else 'secg')
    nodes.append((l, s, doc))
nodes.append(('sect163r1', '24b7b137c8a14d696e6768756151756fd0da2e5c', 'secg'))
def F(s): k = s.find(MQ); return k, s[:k] + s[k+18:]
def related(a, b):
    ka, Fa = F(a); kb, Fb = F(b)
    if ka == kb and sum(x == y for x, y in zip(a, b)) >= 24: return 'same-k, %d/40 nibbles equal' % sum(x == y for x, y in zip(a, b))
    if ka != kb and Fa[2:-3] == Fb[2:-3]: return 'MQ moved %d->%d, filler equal except ends' % (ka, kb)
    return None
adj = {i: [] for i in range(len(nodes))}
for i, j in itertools.combinations(range(len(nodes)), 2):
    r = related(nodes[i][1], nodes[j][1])
    if r: adj[i].append((j, r)); adj[j].append((i, r))
seen = set(); comps = []
for i in range(len(nodes)):
    if i in seen or not adj[i]: continue
    stack, comp = [i], []
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u); comp.append(u); stack += [v for v, _ in adj[u]]
    comps.append(sorted(comp))
for c in comps:
    docs = sorted({nodes[u][2] for u in c})
    print('COMPONENT docs=' + ','.join(docs))
    for u in c: print(f'   {nodes[u][0]:18s} {nodes[u][1]}  [{DOC[nodes[u][2]]}]')
    for u in c:
        for v, r in adj[u]:
            if u < v: print(f'      {nodes[u][0]} -- {nodes[v][0]}: {r}')
single = [nodes[i][0] for i in range(len(nodes)) if not adj[i]]
print('\nSINGLETONS (%d):' % len(single), ' '.join(single))
