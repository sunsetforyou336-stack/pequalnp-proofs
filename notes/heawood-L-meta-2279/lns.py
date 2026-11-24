import sys, time, json, itertools
from threading import Timer
from multiprocessing import Pool
from pysat.solvers import Solver
from rows import E, mis, mint
adj={v:set() for v in range(14)}
for a,b in E: adj[a].add(b); adj[b].add(a)
rows=[(z,1) for z in mint]+[(z,0) for z in mis]; R=len(rows)
def fixed_wires(centers):
    """star circuits of the given centres; returns (#gates, list of row-value tuples)"""
    cost=0; vals=[]
    for c in centers:
        nb=sorted(adj[c])
        cost+= 2 if (0 in nb and 1 in nb) else 3
        o2=None
        if not (0 in nb and 1 in nb):
            vals.append(tuple((z>>nb[0]&1)|(z>>nb[1]&1) for z,_ in rows))
        full=tuple(int(any(z>>v&1 for v in nb)) for z,_ in rows)
        vals.append(full)
        vals.append(tuple(full[r]&(rows[r][0]>>c&1) for r in range(R)))
    return cost, vals
def solve(args):
    centers,TL=args
    cost,fx=fixed_wires(centers)
    N=25-cost
    basev=[tuple(z>>i&1 for z,_ in rows) for i in range(14)]+[tuple((z&1)|(z>>1&1) for z,_ in rows)]+fx
    B=len(basev)
    cnt=[0]
    def nv():
        cnt[0]+=1; return cnt[0]
    cl=[]
    t=[nv() for j in range(N)]
    s0=[[nv() for w in range(B+j)] for j in range(N)]
    s1=[[nv() for w in range(B+j)] for j in range(N)]
    v=[[nv() for r in range(R)] for j in range(N)]
    a=[[nv() for r in range(R)] for j in range(N)]
    b=[[nv() for r in range(R)] for j in range(N)]
    for j in range(N):
        W=B+j
        for s in (s0[j],s1[j]):
            cl.append(list(s))
            for x in range(W):
                for y in range(x+1,W): cl.append([-s[x],-s[y]])
        for x in range(W):
            for y in range(0,x+1): cl.append([-s0[j][x],-s1[j][y]])
        for r in range(R):
            for s,val in ((s0[j],a[j]),(s1[j],b[j])):
                for w in range(W):
                    if w<B: cl.append([-s[w], val[r] if basev[w][r] else -val[r]])
                    else:
                        cl.append([-s[w],-val[r],v[w-B][r]]); cl.append([-s[w],val[r],-v[w-B][r]])
            A,Bv,V,T=a[j][r],b[j][r],v[j][r],t[j]
            cl+= [[-A,-Bv,V],[A,Bv,-V],[-T,A,-V],[-T,Bv,-V],[T,-A,V],[T,-Bv,V]]
    for r,(z,tg) in enumerate(rows): cl.append([v[N-1][r] if tg else -v[N-1][r]])
    for j in range(N-1):
        cl.append([s0[k][B+j] for k in range(j+1,N)]+[s1[k][B+j] for k in range(j+1,N)])
        W=B+j
        for x in range(W):
            for y in range(x):
                cl.append([-s1[j][x],-s1[j+1][y],s0[j+1][W],s1[j+1][W]])
    S=Solver(name="cadical195",bootstrap_with=cl)
    t0=time.time()
    try:
        import pysat
        res=None
        # cadical195 in pysat lacks interrupt; use glucose4 with interrupt for limited solving
        S.delete(); S=Solver(name="glucose4",bootstrap_with=cl)
        tm=Timer(TL,lambda: S.interrupt()); tm.start()
        res=S.solve_limited(expect_interrupt=True); tm.cancel()
    except Exception as e:
        res="ERR "+str(e)
    out=None
    if res is True:
        m=set(x for x in S.get_model() if x>0)
        out=[("and" if t[j] in m else "or",[w for w in range(B+j) if s0[j][w] in m][0],[w for w in range(B+j) if s1[j][w] in m][0]) for j in range(N)]
    return (tuple(centers),N,res,round(time.time()-t0,1),out)
if __name__=="__main__":
    side=sys.argv[1]; j=int(sys.argv[2]); TL=float(sys.argv[3])
    pool=range(7,14) if side=="lines" else range(0,7)
    jobs=[(c,TL) for c in itertools.combinations(pool,j)]
    stat={}
    with Pool(4) as p:
        for cen,N,res,tt,out in p.imap_unordered(solve,jobs):
            print(cen,N,res,tt,flush=True)
            key={True:"SAT",False:"UNSAT",None:"TIMEOUT"}.get(res,str(res)); stat[key]=stat.get(key,0)+1
            if res is True:
                print("FOUND",cen,N,out,flush=True); json.dump([cen,out],open("found_%s_%d.json"%(side,j),"w"))
    print(side,"fixed stars",j,"free gates",sorted(set(25-fixed_wires(c)[0] for c,_ in jobs)),"->",stat,flush=True)
