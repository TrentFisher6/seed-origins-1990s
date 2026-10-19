import re, json, sys
t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
secs = re.split(r'\n\s*\d+\.\d+\.\d+\s+Recommended Parameters (sec[pt]\d+[kr]\d)\n', t)
out = {}
for i in range(1, len(secs), 2):
    name, body = secs[i], secs[i+1]
    body = re.split(r'\n\s*\d+\.\d+\s+Recommended Parameters|\n\s*\d\s+(?:Recommended|Objects)', body)[0]
    d = {}
    def grab(key, pat):
        m = re.search(pat, body)
        if m: d[key] = re.sub(r'[^0-9A-Fa-f]', '', m.group(1)).lower()
    grab('seed', r'\n\s*S\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n')
    grab('a', r'\n\s*a\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n')
    grab('b', r'\n\s*b\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n')
    grab('n', r'\n\s*n\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n')
    grab('h', r'\n\s*h\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n')
    m = re.search(r'\n\s*p\s*=\s*([0-9A-F ]+(?:\n[ \t]+[0-9A-F ]+)*)\n', body)
    if m: d['p'] = re.sub(r'\s', '', m.group(1)).lower()
    m = re.search(r'uncompressed form is:\s*\n\s*G\s*=\s*([0-9A-F \n]+?)\n\s*(?:SEC 2|Finally|\n)', body)
    if m: d['G_uncompressed'] = re.sub(r'[^0-9A-Fa-f]', '', m.group(1)).lower()
    d['has_seed'] = 'seed' in d
    out[name] = d
json.dump({'source': sys.argv[1], 'curves': out}, open(sys.argv[2], 'w'), indent=1)
print(len(out)); print({k:v.get('seed') for k,v in out.items()})
