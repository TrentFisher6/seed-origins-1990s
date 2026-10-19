"""For Certicom point seeds (seedP/seedQ) and curve seeds: validity of last-nibble variants.
Point valid (binary): Tr(x + a + b/x^2) == 0 for x = W(seed). Prime: x^3+ax+b is QR."""
import json, sys, re
sys.path.insert(0, 'scripts')
from verify import W_from_seed
from order import pari
cc = json.load(open('data/agent/certicom.json'))['curves']
def fpoly(ftxt):
    exps = [int(e) for e in re.findall(r'x(\d+)', ftxt.replace(' ', ''))]
    return sum(1 << e for e in exps) | 1
def pt_valid(c, seedhex):
    s = bytes.fromhex(seedhex)
    if c['field'] == 'binary':
        m = int(c['m']); f = fpoly(c['f'])
        x = W_from_seed(s, m, False)
        if x == 0: return False
        pol = 'Mod(1,2)*(' + '+'.join(f'y^{i}' for i in range(m+1) if f >> i & 1) + ')'
        pari(f"g=ffgen({pol},'w)")
        el = lambda v: '(' + '+'.join([f'g^{i}' for i in range(m) if v >> i & 1] or ['0*g']) + ')'
        tr = pari(f"trace({el(x)}+{el(int(c['a'],16))}+{el(int(c['b'],16))}/{el(x)}^2)")
        return int(pari.lift(tr)) == 0 if str(tr) not in ('0',) else True
    else:
        p = int(c['p'], 16); x = W_from_seed(s, p.bit_length())
        a, b = int(c['a'], 16), int(c['b'], 16)
        v = (x**3 + a*x + b) % p
        return v == 0 or pow(v, (p-1)//2, p) == 1
if __name__ == '__main__':
    for name, c in cc.items():
        for k in ('seedP', 'seedQ'):
            s = c.get(k)
            if not s: continue
            pat = ''.join('1' if pt_valid(c, s[:-1] + h) else '.' for h in '0123456789abcdef')
            last = int(s[-1], 16)
            first_valid = pat.index('1') if '1' in pat else None
            print(f"{name:10s} {k} last={s[-1]} {pat}  published is first-valid-from-0: {first_valid == last}   valid-below={pat[:last].count('1')}/{last}")
