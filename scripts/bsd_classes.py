import sys
sys.path.insert(0, 'scripts')
from bsd_random import bsd_random
T = {'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584', 'SEED1994': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd',
     'B-163': '85e25bfe5c86226cdb12016f7553f9d0e693a268', 'XSEED': 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6'}
N = int(sys.argv[1])
for init in (1, 0):
    for c in range(512 if init == 1 else 0):
        o = bsd_random(c, N, init)
        st = bytes(v & 0xff for v in o).hex()
        for name, t in T.items():
            for piece in (t[:12], t[28:]):
                i = st.find(piece)
                while i >= 0:
                    if i % 2 == 0: print('HIT', name, 'class', c, 'init', init, 'byte', i // 2, piece, flush=True)
                    i = st.find(piece, i + 1)
print('done')
