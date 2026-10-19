import hashlib, struct, json, sys
def rol(x,n): return ((x<<n)|(x>>(32-n)))&0xffffffff
def sha0(m):
    h=[0x67452301,0xEFCDAB89,0x98BADCFE,0x10325476,0xC3D2E1F0]
    ml=len(m)*8; m+=b'\x80'
    while len(m)%64!=56: m+=b'\0'
    m+=struct.pack('>Q',ml)
    for i in range(0,len(m),64):
        w=list(struct.unpack('>16I',m[i:i+64]))
        for t in range(16,80): w.append(w[t-3]^w[t-8]^w[t-14]^w[t-16])  # SHA-0: no rotate
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
def sha1(m): return hashlib.sha1(m).digest()
def isprime(n):
    if n<2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%q==0: return n==q
    d=n-1;s=0
    while d%2==0: d//=2;s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53):
        x=pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1: break
        else: return False
    return True
def gen(seed_hex,H,L=512):
    seed=int(seed_hex,16); g=160; n=(L-1)//160; b=(L-1)%160
    I=lambda x:int.from_bytes(x,'big')
    S=lambda v:v.to_bytes(20,'big')
    U=I(H(S(seed)))^I(H(S((seed+1)%2**g)))
    q=U|(1<<159)|1
    if not isprime(q): return None
    counter=0; offset=2
    while counter<4096:
        W=0
        for k in range(n+1):
            V=I(H(S((seed+offset+k)%2**g)))
            if k==n: V&=(1<<b)-1
            W|=V<<(160*k)
        X=W+(1<<(L-1))
        c=X%(2*q); p=X-(c-1)
        if p>=(1<<(L-1)) and isprime(p): return dict(p=p,q=q,counter=counter)
        counter+=1; offset+=n+1
    return None
def findq(seed_hex,H): return gen(seed_hex,H)
if __name__=='__main__':
    out={}
    for name,seed,H in (('fips186_1994_sha0','d5014e4b60ef2ba8b6211b4062ba3224e0427dbd',sha0),('fips186_1994_seed_with_sha1','d5014e4b60ef2ba8b6211b4062ba3224e0427dbd',sha1),('fips186-1_and_2_sha1','d5014e4b60ef2ba8b6211b4062ba3224e0427dd3',sha1)):
        r=gen(seed,H); 
        if r:
            p,q=r['p'],r['q']; 
            r={'p':'%x'%p,'q':'%x'%q,'counter':r['counter'],'g':'%x'%pow(2,(p-1)//q,p)}
        out[name]=r; print(name,r)
    json.dump(out,open(sys.argv[1],'w'),indent=1)
