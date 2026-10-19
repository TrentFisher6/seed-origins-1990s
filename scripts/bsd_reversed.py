"""Last cheap check within the XSEED mechanism: KSEED / SEED94 as unseeded-random() byte streams in reversed byte order
(whole 20-byte reversal, or per-32-bit-word little-endian), byte = (o>>sh)&0xff, sh 0..23, first 1e6 outputs."""
import sys
sys.path.insert(0, 'scripts')
from bsd_random import bsd_random
T = {'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584', 'SEED94': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd'}
def variants(h):
    b = bytes.fromhex(h)
    yield 'rev20', b[::-1].hex()
    yield 'wordLE', b''.join(b[i:i+4][::-1] for i in range(0, 20, 4)).hex()
    yield 'nibswap', ''.join(h[i+1] + h[i] for i in range(0, 40, 2))
pieces = {}
for n, h in T.items():
    for vn, v in variants(h): pieces[v[:10]] = (n, vn); pieces[v[30:]] = (n, vn)
# control: XSEED reversed must be found when we search reversed... check the XSEED forward in stream first
o = bsd_random(1, 1000000)
for sh in range(24):
    st = bytes((v >> sh) & 0xff for v in o).hex()
    if sh == 0: assert st.startswith('bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6')
    for p, lab in pieces.items():
        i = st.find(p)
        while i >= 0:
            if i % 2 == 0: print('HIT', lab, 'shift', sh, 'byte', i // 2, p)
            i = st.find(p, i + 1)
print('done')
