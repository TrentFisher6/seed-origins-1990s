"""SEC 2 v1 sect163r1: published seed does not give b under X9.62, but bit-reversing the 163-bit W does."""
import sys; sys.path.insert(0, 'scripts')
from verify import W_from_seed
seed = '24b7b137c8a14d696e6768756151756fd0da2e5c'           # SEC 2 v1 sect163r1 S (data/agent/raw/sec2/sec2-v1.txt)
b = 0x0713612dcddcb40aab946bda29ca91f73af958afd9             # SEC 2 v1 sect163r1 b
W = W_from_seed(bytes.fromhex(seed), 163, False)
rev = int(bin(W)[2:].zfill(163)[::-1], 2)
print('W        =', hex(W)); print('rev(W)   =', hex(rev)); print('b        =', hex(b))
print('W == b:', W == b, '  bitreverse163(W) == b:', rev == b)
