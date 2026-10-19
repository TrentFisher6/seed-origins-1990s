import re, json, sys
src = open(sys.argv[1]).read()
# map struct names -> data
blocks = re.finditer(r'\}\s*(_EC_\w+)\s*=\s*\{\s*\{\s*(NID_\w+),\s*(\d+),\s*(\d+),\s*(0x[0-9A-Fa-f]+|\d+)\s*\},\s*\{(.*?)\}\s*\};', src, re.S)
curves = {}
for m in blocks:
    name, ft, sl, pl, cof, body = m.groups()
    body = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
    b = bytes(int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{1,2})\b', body))
    sl, pl = int(sl), int(pl)
    assert len(b) >= sl + 6*pl, (name, len(b))
    f = [b[sl+i*pl: sl+(i+1)*pl].hex() for i in range(6)]
    curves[name] = dict(field='prime' if 'prime' in ft else 'binary', seed=b[:sl].hex(), p=f[0], a=f[1], b=f[2], x=f[3], y=f[4], n=f[5], h=int(cof, 0))
# names table
tab = re.findall(r'\{\s*(NID_\w+),\s*&(_EC_\w+)\.h,', src)
out = {}
for nid, s in tab:
    out.setdefault(nid.replace('NID_', ''), curves[s] | {'struct': s})
json.dump(out, open(sys.argv[2], 'w'), indent=1)
for k, v in out.items():
    if v['seed']: print(f"{k:22s} {v['field']:6s} {v['seed']}")
