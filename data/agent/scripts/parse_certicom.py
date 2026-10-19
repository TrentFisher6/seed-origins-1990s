import re, json, sys, html, hashlib
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8', errors='replace').read()
t = re.sub(r'<br\s*/?>', '\n', t)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
curves = {}
cur = None
for line in t.splitlines():
    line = line.strip()
    m = re.match(r'=+\s*(ECC\w*-\d+)\s*=+$', line)
    if m:
        cur = m.group(1); curves[cur] = {}; continue
    if cur and '=' in line:
        k, v = [x.strip() for x in line.split('=', 1)]
        if k.lower() in ('seede','seedp','seedq'): k = 'seed' + k[-1].upper()
        if k in ('x', 'y'):  # some prime entries list point coords as bare x,y: first = P, second = Q
            k = ('P_' if ('P_'+k) not in curves[cur] else 'Q_') + k
        if k in ('f',): curves[cur][k] = v; continue
        if v == 'NO': curves[cur][k] = None; continue
        h = v.replace(' ', '')
        if re.fullmatch(r'[0-9A-Fa-f]+', h): curves[cur][k] = h.lower()
        else: curves[cur][k] = v
for name, c in curves.items():
    c['field'] = 'binary' if name.startswith('ECC2') else 'prime'
    c['koblitz'] = 'K' in name.split('-')[0]
json.dump({'source': 'https://www.certicom.com/en/curves-list (fetched 2026-10-19), same data as appendix of challenge-2009.pdf',
           'note': 'hex strings, lowercase, spaces removed. seedE/seedP/seedQ are 160-bit SHA-1 seeds. m,f as given. f is text polynomial.',
           'curves': curves}, open(out, 'w'), indent=1)
print(len(curves), list(curves))
