"""Control for the 'keyboard-typed' claim: excess of digits 5-9 (z-score) in X9.62/SEC2/Certicom binary 'a' values and base-point x
versus SHA-1-derived values (binary b = W(seed); Certicom U_x/V_x), which are random by construction."""
import json, math
o = json.load(open('data/openssl_curves.json')); cc = json.load(open('data/agent/certicom.json'))['curves']
s2 = json.load(open('data/agent/sec2_v1_params.json'))['curves']
def z(h):
    h = h.lstrip('0'); n = len(h); f = sum(c in '56789' for c in h) / n
    return (f - 5/16) / math.sqrt(5/16 * 11/16 / n)
ctrl = [v['b'] for k, v in o.items() if v['field'] == 'binary' and v['seed'] and not k.startswith('wap')]
ctrl += [v[f] for v in cc.values() if v['field'] == 'binary' for f in ('b', 'U_x', 'V_x') if v.get(f) and v.get('seedE' if f == 'b' else 'seedP')]
test = {k + '.a': v['a'] for k, v in o.items() if v['field'] == 'binary' and int(v['a'], 16) > 1 and not k.startswith('wap')}
test.update({k + '.Gx': v['x'] for k, v in o.items() if not k.startswith('wap')})
test['sect163r1.Gx(SEC2)'] = s2['sect163r1']['G_uncompressed'][2:44]
zc = sorted(z(h) for h in ctrl)
print(f'control (SHA-1-derived, n={len(zc)}): max z = {zc[-1]:.2f}, 95th pct = {zc[int(.95*len(zc))]:.2f}')
over = sorted(((z(h), k) for k, h in test.items()), reverse=True)
print('test values with z above control max:', [(k, round(v, 1)) for v, k in over if v > zc[-1]])
