"""Verify seeds -> curve coefficient per ANSI X9.62 A.3.3 (SHA-1 'verifiably random')."""
import json, hashlib, sys
def sha1(b): return hashlib.sha1(b).digest()

def W_from_seed(seed: bytes, t: int, clear_top=True):
    g = len(seed) * 8
    s = (t - 1) // 160
    h = t - 160 * s
    H = int.from_bytes(sha1(seed), 'big')
    c0 = H & ((1 << h) - 1)
    if clear_top: c0 &= ~(1 << (h - 1))
    W = c0
    z = int.from_bytes(seed, 'big')
    for i in range(1, s + 1):
        Wi = int.from_bytes(sha1(((z + i) % (1 << g)).to_bytes(g // 8, 'big')), 'big')
        W = (W << 160) | Wi
    return W

def check_prime(c):
    p, a, b = (int(c[k], 16) for k in 'pab')
    t = p.bit_length()
    r = W_from_seed(bytes.fromhex(c['seed']), t)
    return (r * b * b - a ** 3) % p == 0

def check_binary(c):
    f = int(c['p'], 16); m = f.bit_length() - 1
    b = int(c['b'], 16)
    for clear in (False, True):
        if W_from_seed(bytes.fromhex(c['seed']), m, clear) == b: return 'b=W' + (' (top bit cleared)' if clear else '')
    return False

if __name__ == '__main__':
    C = json.load(open(sys.argv[1]))
    for k, c in C.items():
        if not c['seed']: continue
        ok = check_prime(c) if c['field'] == 'prime' else check_binary(c)
        print(f"{k:24s} {c['field']:6s} {ok}")
