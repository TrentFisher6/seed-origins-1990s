import json, hashlib, sys
d = json.load(open(sys.argv[1]))['curves']
MQ = bin(int.from_bytes(b'MinghuaQu', 'big'))[2:].zfill(72)
def sha(x): return hashlib.sha1(x.to_bytes(20, 'big')).digest()
def derive(seed, bits, prime):
    s = (bits - 1)//160; h = bits - 160*s
    H = int.from_bytes(sha(seed), 'big')
    c0 = H & ((1 << h) - 1)
    if prime: c0 &= ~(1 << (h-1))
    v = c0
    for i in range(1, s+1):
        v = (v << 160) | int.from_bytes(sha((seed + i) % 2**160), 'big')
    return v
res = {}
for name, c in d.items():
    r = {}
    prime = c['field'] == 'prime'
    bits = int(c['p'], 16).bit_length() if prime else int(c['m'])
    for k in ('seedE', 'seedP', 'seedQ'):
        s = c.get(k)
        if not s: continue
        sb = bin(int(s, 16))[2:].zfill(160)
        off = sb.find(MQ)
        r[k + '_mq_bitoffset_from_msb'] = off
    if prime:
        p = int(c['p'], 16)
        if c.get('seedE'):
            rr = derive(int(c['seedE'], 16), bits, True)
            a, b = int(c['a'], 16), int(c['b'], 16)
            r['seedE_ok'] = (rr == int(c['r'], 16)) and (rr * b * b - a**3) % p == 0
        for k, xk in (('seedP', 'P_x'), ('seedQ', 'Q_x')):
            if c.get(k):
                x = derive(int(c[k], 16), bits, True)
                r[k + '_matches_x_directly'] = (x == int(c[xk], 16))  # P=hU so only valid if h==1
    else:
        if c.get('seedE'):
            bb = derive(int(c['seedE'], 16), bits, False)
            r['seedE_ok'] = (bb == int(c['b'], 16))
        for k, xk in (('seedP', 'U_x'), ('seedQ', 'V_x')):
            if c.get(k):
                r[k + '_ok'] = (derive(int(c[k], 16), bits, False) == int(c[xk], 16))
    res[name] = r
    print(name, r)
json.dump(res, open(sys.argv[2], 'w'), indent=1)
