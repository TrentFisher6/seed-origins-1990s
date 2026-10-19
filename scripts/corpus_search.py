import json, hashlib
C = json.load(open('data/openssl_curves.json'))
MQ = b'MinghuaQu'.hex()
corpus = {}
for k, v in C.items():
    if k.startswith('wap'): continue
    for f in ('seed','p','a','b','x','y','n'):
        if v[f]: corpus[f'{k}.{f}'] = v[f]
    if v['seed']:
        s = bytes.fromhex(v['seed'])
        corpus[f'{k}.sha1(seed)'] = hashlib.sha1(s).hexdigest()
        z = int.from_bytes(s,'big')
        for i in range(1,4): corpus[f'{k}.sha1(seed+{i})'] = hashlib.sha1((z+i).to_bytes(20,'big')).hexdigest()
fills = {}
for k, v in C.items():
    s = v['seed']
    if k.startswith('wap') or not s or MQ not in s: continue
    i = s.find(MQ); fills[k] = (s[:i], s[i+18:])
L = 7
for k, (pre, suf) in fills.items():
    for part in (pre, suf):
        for j in range(len(part)-L+1):
            sub = part[j:j+L]
            for ck, cv in corpus.items():
                if ck.startswith(k+'.'): continue
                if sub in cv: print(k, repr(part), sub, '->', ck)
