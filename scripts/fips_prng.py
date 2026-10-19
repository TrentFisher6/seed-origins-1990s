"""FIPS 186 App.3.1 PRNG chained from XKEY=XSEED (and KKEY): x_j = G(t, XKEY [+XSEED_j]); XKEY = (1+XKEY+x_j) mod 2^160.
Does KSEED / SEED94 / B-163 appear among outputs (raw or mod q), for SHA-0/SHA-1, t in {t_x, t_k}?"""
import sys
sys.path.insert(0, 'scripts')
from g_func import G
V = {'KSEED': 0x687a66d90648f993867e121f4ddf9ddb01205584, 'SEED94': 0xd5014e4b60ef2ba8b6211b4062ba3224e0427dbd,
     'B-163': 0x85e25bfe5c86226cdb12016f7553f9d0e693a268, 'XSEED': 0xbd029bbe7f51960bcf9edb2b61f06f0feb5a38b6}
qs = {'q94': 0xb20db0b101df0c6624fc1392ba55f77d577481e5, 'q186_1': 0xc773218c737ec8ee993b4f2ded30f48edace915f}
T = ['67452301efcdab8998badcfe10325476c3d2e1f0', 'efcdab8998badcfe10325476c3d2e1f067452301']
for start in ('XSEED', 'KSEED'):
    for sha1 in (True, False):
        for t in T:
            key = V[start]
            for j in range(2000):
                x = int.from_bytes(G(t, key.to_bytes(20, 'big'), sha1), 'big')
                for n, v in V.items():
                    if n == start: continue
                    if x == v: print('MATCH raw', start, sha1, t[:4], j, n)
                    for qn, q in qs.items():
                        if x % q == v: print('MATCH modq', qn, start, sha1, t[:4], j, n)
                key = (1 + key + x) % 2**160
print('done')
