"""SECG/X9.62 binary MQ seeds: validity (same a, same cofactor, n prime) when varying the LAST byte or FIRST byte 0x00..0xff.
Is the published value the first valid when scanning up from 0x00 (or from 0x10 for first byte)?"""
import json, sys
sys.path.insert(0, 'scripts')
from scan import valid, C
MQ = b'MinghuaQu'.hex()
names = sys.argv[1:] or [k for k, v in C.items() if v['seed'] and MQ in v['seed'] and v['field'] == 'binary' and not k.startswith('wap')]
for k in names:
    c = C[k]; s = c['seed']; i = s.find(MQ)
    res = {}
    if i + 18 <= 38:
        pat = ''.join('1' if valid(c, s[:-2] + f'{x:02x}') else '.' for x in range(256))
        pub = int(s[-2:], 16); v = [j for j, ch in enumerate(pat) if ch == '1']
        res['last'] = (pub, v.index(pub), len(v))
    if i >= 2:
        pat = ''.join('1' if valid(c, f'{x:02x}' + s[2:]) else '.' for x in range(256))
        pub = int(s[:2], 16); v = [j for j, ch in enumerate(pat) if ch == '1']
        res['first'] = (pub, v.index(pub), len(v), v[:6])
    print(k, s, 'last(pub,rank-among-valid,#valid)=', res.get('last'), ' first=', res.get('first'), flush=True)
