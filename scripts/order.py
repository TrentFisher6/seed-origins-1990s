import json, time, cypari2
pari = cypari2.Pari(); pari.allocatemem(2*10**9, silent=True) if hasattr(pari,'allocatemem') else None
C = json.load(open('data/openssl_curves.json'))
def poly_from_int(f):
    m = f.bit_length()-1
    return 'Mod(1,2)*(' + '+'.join(f'x^{i}' for i in range(m+1) if f >> i & 1) + ')'
def elt(v, g, m):
    return '(' + '+'.join([f'{g}^{i}' for i in range(m) if v >> i & 1] or ['0*'+g]) + ')'
def card_binary(f, a, b):
    m = f.bit_length()-1
    pari(f'g = ffgen({poly_from_int(f)}, \'w)')
    return int(pari(f'ellcard(ellinit([1,{elt(a,"g",m)},0,0,{elt(b,"g",m)}]))'))
def card_prime(p, a, b):
    return int(pari(f'ellcard(ellinit([{a},{b}],{p}))'))
if __name__ == '__main__':
    for k in ['sect113r1','sect131r1','sect193r1','X9_62_c2tnb239v1','secp160r1','secp112r1']:
        c = C[k]; t=time.time()
        f,a,b,n = (int(c[x],16) for x in 'pabn')
        N = card_binary(f,a,b) if c['field']=='binary' else card_prime(f,a,b)
        print(k, N == n*c['h'], N//n if N%n==0 else None, round(time.time()-t,3))
