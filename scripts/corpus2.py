import json, hashlib, sys
sys.path.insert(0,'scripts'); from verify import W_from_seed
MQ = b'MinghuaQu'.hex()
C = json.load(open('data/openssl_curves.json')); cc = json.load(open('data/agent/certicom.json'))['curves']
corpus = {}
for k, v in C.items():
    for f in 'pabxyn': corpus[f'{k}.{f}'] = v[f].lower()
for k, v in cc.items():
    for f, x in v.items():
        if isinstance(x, str) and f not in ('seedE','seedP','seedQ','m','f','field','h'): corpus[f'{k}.{f}'] = x.lower()
seeds = [tuple(x) for x in json.load(open('data/all_seeds.json'))]
for l, s in seeds:
    z = int(s, 16)
    for d in range(-2, 3):
        corpus[f'sha1({l}{d:+d})'] = hashlib.sha1(((z+d) % 2**160).to_bytes(20,'big')).hexdigest()
L = int(sys.argv[1]) if len(sys.argv)>1 else 7
hits = set()
for l, s in seeds:
    i = s.find(MQ)
    if i < 0: continue
    for part in (s[:i], s[i+18:]):
        for j in range(len(part)-L+1):
            sub = part[j:j+L]
            for ck, cv in corpus.items():
                if l in ck: continue
                if sub in cv: hits.add((l, sub, ck))
for h in sorted(hits): print(*h)
# chance estimate: number of substrings x corpus nibbles / 16^L
nsub = sum(max(0,len(p)-L+1) for l,s in seeds if MQ in s for p in (s[:s.find(MQ)], s[s.find(MQ)+18:]))
ncorp = sum(len(v) for v in corpus.values())
print('expected chance hits ~', nsub*ncorp/16**L)
