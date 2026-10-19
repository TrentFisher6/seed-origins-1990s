import json, collections
MQ = b'MinghuaQu'.hex()
seeds = [tuple(x) for x in json.load(open('data/all_seeds.json'))]
seeds = [(l,s) for l,s in seeds if MQ in s]
# for each pair, compute nibble-diff mask
def diffmask(a,b): return ''.join('.' if x==y else 'x' for x,y in zip(a,b))
pairs=[]
for i in range(len(seeds)):
    for j in range(i+1,len(seeds)):
        (la,a),(lb,b)=seeds[i],seeds[j]
        if a.find(MQ)!=b.find(MQ): continue
        same=sum(x==y for x,y in zip(a,b))
        if same>=18+6:
            pairs.append((la,lb,a,b))
            print(f"{la:16s} {lb:16s} {diffmask(a,b)}  same={same}")
