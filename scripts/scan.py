import json, sys
sys.path.insert(0,'scripts')
from verify import W_from_seed
from order import card_binary, card_prime, pari
C = json.load(open('data/openssl_curves.json'))
MQ = b'MinghuaQu'.hex()
def isprime(n): return bool(pari.isprime(n))
def valid(c, seedhex):
    s = bytes.fromhex(seedhex); f=int(c['p'],16); a=int(c['a'],16); h=c['h']
    if c['field']=='binary':
        m=f.bit_length()-1; b=W_from_seed(s,m,False)
        if b==0: return False
        N=card_binary(f,a,b)
    else:
        p=f; r=W_from_seed(s,p.bit_length())
        if r==0: return False
        b2 = a**3*pow(r,-1,p)%p
        if pow(b2,(p-1)//2,p)!=1: return False
        b=int(pari(f'lift(sqrt(Mod({b2},{p})))'))
        N=card_prime(p,a,b)
        # twist counted too
        N2=2*p+2-N
        return (N%h==0 and isprime(N//h)) or (N2%h==0 and isprime(N2//h))
    return N%h==0 and isprime(N//h)
names = sys.argv[1:] or [k for k,v in C.items() if v['seed'] and MQ in v['seed'] and not k.startswith('wap')]
for k in names:
    c=C[k]; s=c['seed']; i=s.find(MQ); F=s[:i]+s[i+18:]
    def mk(F,k_): return F[:k_]+MQ+F[k_:]
    last = ''.join('1' if valid(c, s[:-1]+x) else '.' for x in '0123456789abcdef')
    if c['field']=='binary':
        first = ''.join('1' if valid(c, f'{x:02x}'+s[2:]) else '.' for x in range(256)) if i>=2 else 'n/a'
    else: first='skip'
    pos = ''.join('1' if valid(c, mk(F,kk)) else '.' for kk in range(23))
    print(f"{k:18s} k={i:2d} last[{s[-1]}]={last}  pos={pos}")
    if first not in('n/a','skip'): print(f"   first[{s[:2]}] idx={int(s[:2],16)} valid@{[j for j,ch in enumerate(first) if ch=='1'][:20]}")
    sys.stdout.flush()
