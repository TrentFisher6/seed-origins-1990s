"""Old BSD/SunOS random() (TYPE_3, srandom via x=1103515245*x+12345, discard 310). Default unseeded state == srandom(1)."""
import sys
def bsd_random(seed, n, init=1):
    r = [seed & 0xffffffff]
    for i in range(1, 31):
        if init == 1: r.append((1103515245 * r[i-1] + 12345) & 0xffffffff)
        else:
            hi, lo = divmod(r[i-1], 127773); w = 16807 * lo - 2836 * hi
            r.append(w + 2147483647 if w < 0 else w)
    for i in range(31, 34): r.append(r[i-31])
    for i in range(34, 344 + n): r.append((r[i-31] + r[i-3]) & 0xffffffff)
    return [r[k+344] >> 1 for k in range(n)]
if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    o = bsd_random(seed, 200000)
    targets = {'XSEED': 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6', 'KSEED': '687a66d90648f993867e121f4ddf9ddb01205584',
               'SEED1994': 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd', 'B-163': '85e25bfe5c86226cdb12016f7553f9d0e693a268'}
    print('first 20 bytes random()&0xff:', bytes(v & 0xff for v in o[:20]).hex())
    for sh in range(24):
        st = bytes((v >> sh) & 0xff for v in o).hex()
        for name, t in targets.items():
            for half in (t, t[:16], t[24:]):
                i = st.find(half)
                if i >= 0 and i % 2 == 0: print(f'{name} piece {half} at byte {i//2} with (random()>>{sh})&0xff')
    # 32-bit words / 31-bit words printed
    w8 = ''.join('%08x' % v for v in o[:50000])
    for name, t in targets.items():
        if t[:8] in w8: print(name, 'in %08x words at', w8.find(t[:8]) / 8)
