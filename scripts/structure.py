import json, itertools
C = json.load(open('data/openssl_curves.json'))
MQ = b'MinghuaQu'.hex()
rows = {}
for k, v in C.items():
    s = v['seed']
    if not s or k.startswith('wap'): continue
    i = s.find(MQ)
    if i < 0: continue
    F = s[:i] + s[i+18:]
    rows[k] = (i, F)
    print(f"{k:18s} k={i:2d}  {s[:i]:>22s}|MQ|{s[i+18:]:<22s}  F={F}")
# shared substrings between fillers
print()
def lcs(a, b):
    best = (0, '')
    for i in range(len(a)):
        for j in range(len(b)):
            l = 0
            while i+l < len(a) and j+l < len(b) and a[i+l] == b[j+l]: l += 1
            if l > best[0]: best = (l, a[i:i+l])
    return best
for (a, (ia, Fa)), (b, (ib, Fb)) in itertools.combinations(rows.items(), 2):
    l, s = lcs(Fa, Fb)
    if l >= 4: print(a, b, l, s)
