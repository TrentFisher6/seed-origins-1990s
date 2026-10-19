import json, hashlib, sys, re
MQ = bin(int.from_bytes(b'MinghuaQu','big'))[2:].zfill(72)
def sha(x): return hashlib.sha1(x.to_bytes(20,'big')).digest()
def derive(seed, bits, prime):
    s=(bits-1)//160; h=bits-160*s
    c0=int.from_bytes(sha(seed),'big') & ((1<<h)-1)
    if prime: c0 &= ~(1<<(h-1))
    v=c0
    for i in range(1,s+1): v=(v<<160)|int.from_bytes(sha((seed+i)%2**160),'big')
    return v
d=json.load(open(sys.argv[1]))['curves']; res={}
for n,c in d.items():
    if not c.get('seed'): continue
    seed=int(c['seed'],16); sb=bin(seed)[2:].zfill(160); off=sb.find(MQ)
    r={'mq_bitoffset':off}
    if n.startswith('secp'):
        p=int(c['p'],16); t=p.bit_length()
        cc=derive(seed,t,True); b=int(c['b'],16)
        a=int(c['a'],16); r['ok']=(b*b*cc-a**3)%p==0
    else:
        m=int(re.match(r'sect(\d+)',n).group(1))
        r['ok']=derive(seed,m,False)==int(c['b'],16)
    res[n]=r
    c['verified_sha1_x962']=r['ok']; c['mq_bitoffset_in_seed']=off
json.dump({'source':sys.argv[1],'curves':d},open(sys.argv[1],'w'),indent=1)
print({k:(v['ok'],v['mq_bitoffset']) for k,v in res.items()})
