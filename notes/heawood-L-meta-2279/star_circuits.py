from rows import E
adj={v:set() for v in range(14)}
for a,b in E: adj[a].add(b); adj[b].add(a)
def f(z): return any(z>>a&1 and z>>b&1 for a,b in E)
def run(gates,free):
    for z in range(1<<14):
        w=[z>>i&1 for i in range(14)]+([ (z&1)|(z>>1&1) ] if free else [])
        for op,a,b in gates: w.append(w[a]&w[b] if op=="and" else w[a]|w[b])
        if bool(w[-1])!=f(z): return False
    return True
def star_circuit(centers,free):
    B=15 if free else 14
    gates=[]; outs=[]
    for c in centers:
        nb=sorted(adj[c])
        if free and 0 in nb and 1 in nb:
            rest=[v for v in nb if v not in (0,1)][0]
            gates.append(("or",14,rest))
        else:
            gates.append(("or",nb[0],nb[1])); gates.append(("or",B+len(gates)-1,nb[2]))
        gates.append(("and",c,B+len(gates)-1)); outs.append(B+len(gates)-1)
    cur=outs[0]
    for o in outs[1:]:
        gates.append(("or",cur,o)); cur=B+len(gates)-1
    return gates
for label,centers,free in [("point-centred stars",range(7),False),("line-centred stars",range(7,14),False),("line-centred stars + free OR",range(7,14),True)]:
    g=star_circuit(list(centers),free)
    print(label,": gates",len(g),"correct" if run(g,free) else "WRONG")
print("pairs sharing >=2 neighbours:",sum(1 for u in range(14) for v in range(u+1,14) if len(adj[u]&adj[v])>=2))
print("pairs sharing exactly 1 neighbour:",sum(1 for u in range(14) for v in range(u+1,14) if len(adj[u]&adj[v])==1))
