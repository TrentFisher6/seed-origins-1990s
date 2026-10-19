"""FreeLIP zrandom: s <- s*3^121 mod (2^107-1); limb = s mod 2^26. Recover s from consecutive known limbs (any bit alignment
in a 160-bit seed) via LLL, then walk back looking for a small zrstarts seed."""
import sys, cypari2
pari = cypari2.Pari()
M = 2**107 - 1; A = pow(3, 121, M); AI = pow(A, -1, M); K = 1 << 26; KI = pow(K, -1, M); HB = 1 << 81
def recover(limbs):
    n = len(limbs)
    a = [pow(A, i, M) for i in range(n)]
    d = [((a[i] * limbs[0] - limbs[i]) * KI) % M for i in range(n)]
    # h_i = a_i h_0 + d_i (mod M)
    basis = [[1] + a[1:] + [0]] + [[0]*j + [M] + [0]*(n-j) for j in range(1, n)] + [[0] + d[1:] + [HB]]
    Mt = pari.matrix(n+1, n+1, [basis[r][c] for c in range(n+1) for r in range(n+1)])
    R = Mt * pari.qflll(Mt)
    out = []
    for col in range(n+1):
        v = [int(R[r, col]) for r in range(n+1)]
        if abs(v[-1]) != HB: continue
        if v[-1] < 0: v = [-t for t in v]
        h0 = v[0]
        if 0 <= h0 < HB:
            s = (K * h0 + limbs[0]) % M
            x, ok = s, True
            for i in range(n):
                if x % K != limbs[i]: ok = False; break
                x = x * A % M
            if ok: out.append(s)
    return out
def walk_back(s, steps=2_000_000, small=1 << 40):
    for k in range(steps):
        if s < small: return k, s
        s = s * AI % M
    return None
def sweep(lab, hx):
    bits = bin(int(hx, 16))[2:].zfill(len(hx) * 4)
    for off in range(26):
        limbs = [int(bits[off+26*j: off+26*(j+1)], 2) for j in range((len(bits) - off) // 26)]
        if len(limbs) < 5: continue
        for s in recover(limbs):
            print('HIT', lab, 'off', off, hex(s), walk_back(s), flush=True)
if __name__ == '__main__':
    # planted control: zrstarts(20000), 7 draws, then zrandomb(2^160) = 8 limbs top-first, mod 2^160
    s = 20000
    def limb():
        global s
        s = s * A % M; return s % K
    for _ in range(7): limb()
    x = 0
    for _ in range(8): x = x << 26 | limb()
    planted = f'{x % 2**160:040x}'
    sweep('PLANT', planted)
    for lab, hx in [('DSA1994_SEED','d5014e4b60ef2ba8b6211b4062ba3224e0427dbd'), ('DSA_XSEED','bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6'),
                    ('DSA_KSEED','687a66d90648f993867e121f4ddf9ddb01205584'), ('B-163','85e25bfe5c86226cdb12016f7553f9d0e693a268')]:
        sweep(lab, hx)
    print('done')
