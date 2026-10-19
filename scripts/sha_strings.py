"""Are MQ fillers pieces of SHA-1 / SHA-0-free hashes of simple strings+counters? 10-nibble window matching anywhere in digest."""
import json, hashlib, sys, struct
MQ = b'MinghuaQu'.hex()
L = 10
win = {}
for l, s in json.load(open('data/all_seeds.json')):
    k = s.find(MQ)
    if k < 0: continue
    for part in (s[:k], s[k+18:], s[:k] + s[k+18:]):
        for j in range(len(part) - L + 1): win.setdefault(part[j:j+L], l)
# planted control
win.setdefault(hashlib.sha1(b'MinghuaQu12345').hexdigest()[3:3+L], 'PLANT')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300000
fams = {
 'dec': lambda i: str(i).encode(),
 'be4': lambda i: struct.pack('>I', i), 'le4': lambda i: struct.pack('<I', i),
 'MQdec': lambda i: b'MinghuaQu' + str(i).encode(), 'MQ_dec': lambda i: b'Minghua Qu' + str(i).encode(),
 'decMQ': lambda i: str(i).encode() + b'MinghuaQu', 'MQbe4': lambda i: b'MinghuaQu' + struct.pack('>I', i),
 'MQpad20': lambda i: b'MinghuaQu' + i.to_bytes(11, 'big'), 'Certicom': lambda i: b'Certicom' + str(i).encode(),
 'seed20': lambda i: i.to_bytes(20, 'big'),
}
hits = 0
for name, f in fams.items():
    for i in range(N):
        h = hashlib.sha1(f(i)).hexdigest()
        for j in range(41 - L):
            w = h[j:j+L]
            if w in win: print('HIT', name, i, j, w, win[w], flush=True); hits += 1
print('done', hits, 'windows', len(win))
