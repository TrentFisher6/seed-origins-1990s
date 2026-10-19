import sys, struct
sys.path.insert(0, 'scripts')
import dsa_scan
def rol(x,n): return ((x<<n)|(x>>(32-n)))&0xffffffff
def sha0(m):
    h=[0x67452301,0xEFCDAB89,0x98BADCFE,0x10325476,0xC3D2E1F0]
    ml=len(m)*8; m+=b'\x80'
    while len(m)%64!=56: m+=b'\0'
    m+=struct.pack('>Q',ml)
    for i in range(0,len(m),64):
        w=list(struct.unpack('>16I',m[i:i+64]))
        for t in range(16,80): w.append(w[t-3]^w[t-8]^w[t-14]^w[t-16])
        a,b,c,d,e=h
        for t in range(80):
            if t<20: f=(b&c)|(~b&d); k=0x5A827999
            elif t<40: f=b^c^d; k=0x6ED9EBA1
            elif t<60: f=(b&c)|(b&d)|(c&d); k=0x8F1BBCDC
            else: f=b^c^d; k=0xCA62C1D6
            tmp=(rol(a,5)+(f&0xffffffff)+e+k+w[t])&0xffffffff
            a,b,c,d,e=tmp,a,rol(b,30),c,d
        h=[(x+y)&0xffffffff for x,y in zip(h,[a,b,c,d,e])]
    return struct.pack('>5I',*h)
assert sha0(b'abc').hex()=='0164b8a914cd2a5e74c4f7ff082c4d97f1edf880'
H0 = lambda x: int.from_bytes(sha0(x.to_bytes(20,'big')),'big')
base=int(sys.argv[1],16); lo,hi=int(sys.argv[2]),int(sys.argv[3])
for i in range(lo,hi):
    r=dsa_scan.gen((base+i)%2**160, H=H0)
    if r is not None: print(f'{base+i:040x} i={i:+d}', r if isinstance(r,str) else f'counter={r[0]}')
