E=[(0,7),(0,8),(0,10),(1,7),(1,9),(1,13),(2,8),(2,12),(2,13),(3,7),(3,11),(3,12),(4,10),(4,11),(4,13),(5,9),(5,10),(5,12),(6,8),(6,9),(6,11)]
adj={v:set() for v in range(14)}
for a,b in E: adj[a].add(b); adj[b].add(a)
def f(z): return any(z>>a&1 and z>>b&1 for a,b in E)
mis=[]
for z in range(1<<14):
    if f(z): continue
    if all((z>>v&1) or any(z>>u&1 for u in adj[v]) for v in range(14)): mis.append(z)
mint=[(1<<a)|(1<<b) for a,b in E]
if __name__=="__main__":
    print(len(mis),"maximal independent sets;",len(mint),"edges")
    from collections import Counter
    print(Counter(bin(z).count('1') for z in mis))
