"""Cross-check every constant used against the archived document texts (data/agent/raw/*, extracted with pdftotext by the
research agent), and check FIPS example constants by internal consistency (recompute printed p,q,x,k)."""
import json, re, sys, io, contextlib
sys.path.insert(0, 'scripts')
from g_func import G
import reproduce_exact as R, hashlib
def gen(seed, H=None):
    if H is not None: R.H = H
    try: return R.dsa_gen(seed)
    finally: R.H = lambda x: int.from_bytes(hashlib.sha1(x.to_bytes(20,'big')).digest(),'big')
import sha0 as S0
def chunks_in(h, doc, n=16): return all(h[i:i+n] in doc for i in range(0, len(h), n))  # tolerate page numbers inside long values
def norm(path): return re.sub(r'[^0-9a-z]', '', open(path, errors='ignore').read().lower().replace('l', '1').replace('o', '0'))
# Note: OCR in the 1994 scan turns 1 into l; norm maps l->1 and o->0 (so only hex digits survive meaningfully).
F94, F1, F2 = (norm(f'data/agent/raw/fips/{f}.txt') for f in ('fipspub186-legacy', 'fips186-1-csrc', 'fips186-2'))
SEC2, CERT = norm('data/agent/raw/sec2/sec2-v1.txt'), norm('data/agent/raw/certicom/ch09.txt')
c = {'SEED94': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd', 'SEED1': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dd3',
     'XSEED': 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6', 'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584'}
for k, v in c.items(): print(f'{k:7s} in FIPS186(1994) {v in F94}  186-1 {v in F1}  186-2 {v in F2}')
H0 = lambda x: int.from_bytes(S0.sha0(x.to_bytes(20, 'big')), 'big')
r94 = gen(int(c['SEED94'], 16), H=H0); r1 = gen(int(c['SEED1'], 16))
print('1994: counter', r94[0], 'q in text', '%040x' % r94[1] in F94, 'p in text (16-hex chunks)', chunks_in('%0128x' % r94[2], F94))
print('186-1: counter', r1[0], 'q in text', '%040x' % r1[1] in F1, 'p in text (16-hex chunks)', chunks_in('%0128x' % r1[2], F1), '| in 186-2:', chunks_in('%0128x' % r1[2], F2))
t1, t2 = '67452301efcdab8998badcfe10325476c3d2e1f0', 'efcdab8998badcfe10325476c3d2e1f067452301'
for nm, key, t, sha1, q, doc in [('x94', 'XSEED', t1, False, r94[1], F94), ('k94', 'KSEED', t2, False, r94[1], F94),
                                  ('x186-1', 'XSEED', t1, True, r1[1], F1), ('k186-1', 'KSEED', t2, True, r1[1], F1)]:
    v = '%040x' % (int.from_bytes(G(t, bytes.fromhex(c[key]), sha1), 'big') % q)
    print(f'{nm}: G(t,{key}) mod q = {v} printed in doc: {v in doc}')
MQ = b'MinghuaQu'.hex()
o = json.load(open('data/openssl_curves.json'))
bad = [k for k, v in o.items() if v['seed'] and MQ in v['seed'] and not k.startswith('wap') and v['seed'] not in SEC2 and not k.startswith('X9')]
print('SECG MQ seeds (OpenSSL) not found in SEC 2 v1 text:', bad)
s163 = '24b7b137c8a14d696e6768756151756fd0da2e5c'; print('sect163r1 seed in SEC 2 v1 text:', s163 in SEC2)
cc = json.load(open('data/agent/certicom.json'))['curves']
miss = [(k, f) for k, v in cc.items() for f in ('seedE', 'seedP', 'seedQ') if v.get(f) and v[f].lower() not in CERT]
tot = sum(1 for v in cc.values() for f in ('seedE', 'seedP', 'seedQ') if v.get(f))
print(f'Certicom seeds: {tot} total, missing from challenge-2009 PDF text: {miss}')
