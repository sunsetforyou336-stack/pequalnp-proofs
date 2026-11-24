from itertools import combinations
from rows import E
# every 2-factor of the Heawood graph = complement of a perfect matching (graph is cubic)
adj={v:set() for v in range(14)}
for a,b in E: adj[a].add(b); adj[b].add(a)
def matchings(rem, cur):
    if not rem: yield list(cur); return
    v=min(rem)
    for u in adj[v]:
        if u in rem:
            yield from matchings(rem-{v,u}, cur+[(v,u)])
res={}
n=0
for M in matchings(frozenset(range(14)),[]):
    n+=1
    ms=set(map(frozenset,M))
    g={v:[u for u in adj[v] if frozenset((u,v)) not in ms] for v in range(14)}
    seen=set(); cyc=[]
    for s in range(14):
        if s in seen: continue
        L=0; prev=None; cur=s
        while True:
            seen.add(cur); L+=1
            nxt=[u for u in g[cur] if u!=prev][0]
            prev,cur=cur,nxt
            if cur==s: break
        cyc.append(L)
    k=tuple(sorted(cyc)); res[k]=res.get(k,0)+1
print("perfect matchings:",n,"cycle types of the 2-factors:",res)
