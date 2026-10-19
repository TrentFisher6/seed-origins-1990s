"""Standalone (stdlib only) reproduction of the exact results of round 1.
1. FIPS 186 (1994) XSEED == FIPS 186-1/186-2 XKEY == first 20 bytes of (random() & 0xff) from an unseeded 4.3BSD/SunOS random().
2. FIPS 186-1 DSA SEED == 1994 SEED + 22 == first SEED >= the 1994 SEED whose SHA-1 q is prime; p is found at counter 105."""
import hashlib, random as _r

def bsd_random(seed, n):
    r = [seed & 0xffffffff]
    for i in range(1, 31): r.append((1103515245 * r[i-1] + 12345) & 0xffffffff)
    for i in range(31, 34): r.append(r[i-31])
    for i in range(34, 344 + n): r.append((r[i-31] + r[i-3]) & 0xffffffff)
    return [r[k+344] >> 1 for k in range(n)]

def is_prime(n, rounds=40):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    rng = _r.Random(1)
    for _ in range(rounds):
        x = pow(rng.randrange(2, n - 1), d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def H(x): return int.from_bytes(hashlib.sha1(x.to_bytes(20, 'big')).digest(), 'big')

def dsa_gen(seed, L=512):
    M = 1 << 160
    q = (H(seed) ^ H((seed + 1) % M)) | (1 << 159) | 1
    if not is_prime(q): return None
    n, b, offset = (L - 1) // 160, (L - 1) % 160, 2
    for counter in range(4096):
        V = [H((seed + offset + k) % M) for k in range(n + 1)]
        W = sum(V[k] << (160 * k) for k in range(n)) + ((V[n] % (1 << b)) << (160 * n))
        X = W + (1 << (L - 1)); p = X - (X % (2 * q) - 1)
        if p >= 1 << (L - 1) and is_prime(p): return counter, q, p
        offset += n + 1
    return 'q only'

if __name__ == '__main__':
    xs = bytes(v & 0xff for v in bsd_random(1, 20)).hex()
    print('unseeded BSD random()&0xff x20 :', xs)
    print('FIPS 186 XSEED / 186-1 XKEY     : bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6', xs == 'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6')
    base = 0xd5014e4b60ef2ba8b6211b4062ba3224e0427dbd
    for i in range(0, 40):
        r = dsa_gen(base + i)
        if r is not None:
            print(f'first SHA-1-valid SEED >= 1994 SEED: {base+i:040x} (= +{i}), counter={r[0]}, q={r[1]:x}')
            print('published 186-1: SEED d5014e4b60ef2ba8b6211b4062ba3224e0427dd3 counter 105 q c773218c737ec8ee993b4f2ded30f48edace915f')
            break
