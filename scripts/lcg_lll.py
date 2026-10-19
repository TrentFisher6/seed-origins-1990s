"""Recover lrand48 48-bit state from known top-w-bit windows of outputs at given indices, via LLL (PARI qflll)."""
import cypari2, sys
pari = cypari2.Pari()
A, C, M = 0x5DEECE66D, 0xB, 1 << 48
AINV = pow(A, -1, M)
def step(x): return (A * x + C) % M
def back(x): return ((x - C) * AINV) % M
def coeffs(i):  # x_i = a*x0 + c
    a, c = 1, 0
    for _ in range(i): a, c = (A * a) % M, (A * c + C) % M
    return a, c
def recover(known, w=8):
    """known: dict index->top-w-bit value. returns list of candidate x0."""
    idx = sorted(known); i0 = idx[0]
    sh = 48 - w; B = 1 << sh
    # relative to x_{i0}
    rows = []
    n = len(idx)
    a_c = [coeffs(i - i0) for i in idx]
    H = [known[i] << sh for i in idx]
    d = [(a * H[0] + c - H[j]) % M for j, (a, c) in enumerate(a_c)]
    # basis vectors (as rows): dimension n+1
    basis = []
    basis.append([1] + [a_c[j][0] for j in range(1, n)] + [0])
    for j in range(1, n):
        r = [0] * (n + 1); r[j] = M; basis.append(r)
    basis.append([0] + d[1:] + [B])
    Mt = pari.matrix(n + 1, n + 1, [basis[r][c] for c in range(n + 1) for r in range(n + 1)])  # columns = basis vectors
    R = Mt * pari.qflll(Mt)
    cands = []
    for col in range(n + 1):
        v = [int(R[r, col]) for r in range(n + 1)]
        if abs(v[-1]) != B: continue
        if v[-1] < 0: v = [-t for t in v]
        y0 = v[0]
        if 0 <= y0 < B:
            x = H[0] + y0
            # verify
            ok = True
            for j, i in enumerate(idx):
                xi = x
                for _ in range(i - i0): xi = step(xi)
                if xi >> sh != known[i]: ok = False; break
            if ok:
                for _ in range(i0): x = back(x)
                cands.append(x)
    return cands
def find_srand(x, maxback=1 << 22):
    for k in range(maxback):
        if x & 0xFFFF == 0x330E: return k, x >> 16
        x = back(x)
    return None
if __name__ == '__main__':
    # planted control: srand48(t), skip 37 draws, take 20 bytes lrand48()>>23, insert MQ at nibble 7
    import time
    t = 880000000  # 1997-11-20
    x = (t << 16) | 0x330E
    for _ in range(37): x = step(x)
    out = []
    for _ in range(20): x = step(x); out.append(x >> 40)
    s = bytes(out).hex(); MQ = b'MinghuaQu'.hex()
    seed = (s[:7] + MQ + s[7:])[:40]
    F = seed[:7] + seed[25:]
    known = {i: int(F[2*i:2*i+2], 16) for i in range(11)}
    c = recover(known)
    print('planted seed', seed, 'cands', [hex(v) for v in c])
    for v in c: print('  srand back:', find_srand(v), 'expected t', t, 'steps', 37+1)
