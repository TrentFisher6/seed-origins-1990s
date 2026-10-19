"""FIPS 186 App.3 G(t,c): SHA-0/SHA-1 compression of c||0-pad (512-bit block) with IV=t, no length padding. Test whether
KSEED / SEED / x / k relate to XSEED etc. via G or plain hashes."""
import struct, hashlib, itertools
def rol(x,n): return ((x<<n)|(x>>(32-n)))&0xffffffff
def compress(iv, block, sha1=True):
    w=list(struct.unpack('>16I',block))
    for t in range(16,80):
        v=w[t-3]^w[t-8]^w[t-14]^w[t-16]; w.append(rol(v,1) if sha1 else v)
    a,b,c,d,e=iv
    for t in range(80):
        if t<20: f=(b&c)|(~b&d); k=0x5A827999
        elif t<40: f=b^c^d; k=0x6ED9EBA1
        elif t<60: f=(b&c)|(b&d)|(c&d); k=0x8F1BBCDC
        else: f=b^c^d; k=0xCA62C1D6
        tmp=(rol(a,5)+(f&0xffffffff)+e+k+w[t])&0xffffffff
        a,b,c,d,e=tmp,a,rol(b,30),c,d
    return b''.join(struct.pack('>I',(x+y)&0xffffffff) for x,y in zip(iv,[a,b,c,d,e]))
def G(t_hex, c_bytes, sha1=True):
    iv=list(struct.unpack('>5I',bytes.fromhex(t_hex)))
    return compress(iv, c_bytes.ljust(64,b'\0'), sha1)
V={'XSEED':'bd029bbe7f51960bcf9edb2b61f06f0feb5a38b6','KSEED':'687a66d90648f993867e121f4ddf9ddb01205584',
   'SEED94':'d5014e4b60ef2ba8b6211b4062ba3224e0427dbd','x186_1':'2070b3223dba372fde1c0ffc7b2e3b498b260614',
   'k186_1':'358dad571462710f50e254cf1a376b2bdeaadfbf','B163':'85e25bfe5c86226cdb12016f7553f9d0e693a268'}
T=['67452301efcdab8998badcfe10325476c3d2e1f0','efcdab8998badcfe10325476c3d2e1f067452301']
targets={v:k for k,v in V.items()}
if __name__ == "__main__":
  pass
for (n,h) in (V.items() if __name__ == "__main__" else []):
    b=bytes.fromhex(h)
    outs={}
    for sha1 in (True,False):
        for t in T: outs[f'G{"1" if sha1 else "0"}({t[:4]},{n})']=G(t,b,sha1).hex()
    outs[f'sha1({n})']=hashlib.sha1(b).hexdigest()
    z=int(h,16)
    for d in (1,2,-1): outs[f'sha1({n}{d:+d})']=hashlib.sha1(((z+d)%2**160).to_bytes(20,'big')).hexdigest()
    for k,o in outs.items():
        if o in targets: print('MATCH', k, '=', targets[o])
        for tn,tv in V.items():
            if tv[:8] in o: print('partial', k, tn)
if __name__ == '__main__': print('done')
