"""SHA-0 / SHA-1 of counters and short strings vs DSA KSEED, SEED94 (and B-163, XSEED as control-free extras). Full 160-bit equality."""
import sys, struct, hashlib
sys.path.insert(0, 'scripts')
from sha0 import sha0
T = {'687a66d90648f993867e121f4ddf9ddb01205584': 'KSEED', 'd5014e4b60ef2ba8b6211b4062ba3224e0427dbd': 'SEED94',
     '85e25bfe5c86226cdb12016f7553f9d0e693a268': 'B-163'}
assert sha0(b'abc').hex() == '0164b8a914cd2a5e74c4f7ff082c4d97f1edf880'
N = int(sys.argv[1])
fams = {'dec': lambda i: str(i).encode(), 'be4': lambda i: struct.pack('>I', i), 'be20': lambda i: i.to_bytes(20, 'big'),
        'le4': lambda i: struct.pack('<I', i)}
words = [b'', b'NIST', b'DSA', b'DSS', b'seed', b'SEED', b'KSEED', b'XSEED', b'NSA', b'test', b'example']
for name, f in fams.items():
    for i in range(N):
        m = f(i)
        for h in (sha0(m).hex(), hashlib.sha1(m).hexdigest()):
            if h in T: print('MATCH', name, i, T[h])
for w in words:
    for i in range(min(N, 2000)):
        for m in (w + str(i).encode(), w + b' ' + str(i).encode(), w):
            for h in (sha0(m).hex(), hashlib.sha1(m).hexdigest()):
                if h in T: print('MATCH', m, T[h])
print('done')
