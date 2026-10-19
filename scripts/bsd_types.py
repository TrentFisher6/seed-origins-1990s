"""4.3BSD random() with initstate TYPE_1..4 (deg/sep 7/3, 15/1, 31/3, 63/1), LCG srandom init, pointer-faithful simulation.
Search low-byte / low-nibble streams of all seed classes (mod 512) for DSA KSEED/SEED94, B-163 and MQ fillers."""
import sys, json
TYPES = {1: (7, 3), 2: (15, 1), 3: (31, 3), 4: (63, 1)}
def stream(seed, typ, n):
    deg, sep = TYPES[typ]
    st = [seed & 0xffffffff]
    for i in range(1, deg): st.append((1103515245 * st[i-1] + 12345) & 0xffffffff)
    f, r = sep, 0
    out = []
    for k in range(10 * deg + n):
        st[f] = (st[f] + st[r]) & 0xffffffff
        v = st[f] >> 1
        f = (f + 1) % deg; r = (r + 1) % deg
        if k >= 10 * deg: out.append(v)
    return out
assert bytes(v & 0xff for v in stream(1, 3, 20)).hex() == 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6'   # control: XSEED
MQ = b'MinghuaQu'.hex(); L = 10
win = {}
for l, s in json.load(open('data/all_seeds.json')):
    k = s.find(MQ)
    if k < 0: continue
    for part in (s[:k], s[k+18:], s[:k] + s[k+18:]):
        for j in range(len(part) - L + 1): win.setdefault(part[j:j+L], l)
for n, t in {'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584', 'SEED94': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd',
             'B-163': '85e25bfe5c86226cdb12016f7553f9d0e693a268'}.items():
    win[t[:10]] = n; win[t[30:]] = n
N = int(sys.argv[1])
for typ in (1, 2, 4, 3):
    for c in range(512):
        o = stream(c, typ, N)
        for nm, st in (('byte', bytes(v & 0xff for v in o).hex()), ('nib', ''.join('%x' % (v & 15) for v in o) if c < 32 else '')):
            for j in range(len(st) - L + 1):
                if st[j:j+L] in win: print('HIT type', typ, 'class', c, nm, j, st[j:j+L], win[st[j:j+L]], flush=True)
    print('type', typ, 'done', flush=True)
