"""FIPS 186 App.2 DSA p,q generation. Scan SEED = base+i and report which give valid (q,p) and the counter."""
import hashlib, sys, cypari2
pari = cypari2.Pari()
def isprime(n): return bool(pari.ispseudoprime(n))
def sha1(x): return int.from_bytes(hashlib.sha1(x.to_bytes(20, 'big')).digest(), 'big')
def gen(seed, L=512, H=sha1, maxc=4096):
    g = 160; M = 1 << g
    U = H(seed) ^ H((seed + 1) % M)
    q = U | (1 << 159) | 1
    if not isprime(q): return None
    n = (L - 1) // 160; b = (L - 1) - n * 160
    offset = 2
    for counter in range(maxc):
        V = [H((seed + offset + k) % M) for k in range(n + 1)]
        W = sum(V[k] << (160 * k) for k in range(n)) + ((V[n] % (1 << b)) << (160 * n))
        X = W + (1 << (L - 1))
        c = X % (2 * q); p = X - (c - 1)
        if p >= (1 << (L - 1)) and isprime(p): return counter, q, p
        offset += n + 1
    return 'q-only'
if __name__ == '__main__':
    base = int(sys.argv[1], 16); lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for i in range(lo, hi):
        r = gen((base + i) % (1 << 160))
        tag = '' if r is None else (r if isinstance(r, str) else f'counter={r[0]} q={r[1]:x}')
        if r is not None: print(f'{base+i:040x} i={i:+d} {tag}')
