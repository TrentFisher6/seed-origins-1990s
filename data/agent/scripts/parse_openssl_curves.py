import re, json, sys
src=open(sys.argv[1],encoding='utf-8',errors='replace').read()
MQ='4d696e6768756151'+'75'
pat=re.compile(r'\}\s*_EC_(\w+)\s*=\s*\{\s*\{\s*(NID_\w+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\},\s*\{(.*?)\}\s*\};',re.S)
out={}
for m in pat.finditer(src):
    name,fld,sl,pl,cof,body=m.groups(); sl,pl=int(sl),int(pl)
    bs=bytes(int(x,16) for x in re.findall(r'0x([0-9A-Fa-f]{2})',re.sub(r'/\*.*?\*/','',body,flags=re.S)))
    if len(bs)!=sl+6*pl: continue
    f=lambda i: bs[sl+i*pl:sl+(i+1)*pl].hex()
    d={'field':'prime' if 'prime' in fld else 'binary','cofactor':int(cof),'seed':bs[:sl].hex() or None,
       'p_or_poly':f(0),'a':f(1),'b':f(2),'Gx':f(3),'Gy':f(4),'n':f(5)}
    if d['seed']:
        d['contains_MinghuaQu_hex']=MQ in d['seed']
        sb=bin(int(d['seed'],16))[2:].zfill(160); o=sb.find(bin(int.from_bytes(b'MinghuaQu','big'))[2:].zfill(72)); d['mq_bitoffset']=o
    out[name]=d
json.dump({'source':'OpenSSL 3.0 crypto/ec/ec_curve.c (raw/other/openssl_ec_curve.c)','curves':out},open(sys.argv[2],'w'),indent=1)
for k,v in out.items(): print(k,v['seed'],v.get('mq_bitoffset'))
