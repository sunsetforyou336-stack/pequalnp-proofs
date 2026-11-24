import sys, random, time, json
from pysat.solvers import Solver
from pysat.card import CardEnc
from rows import E, mis, mint
N=int(sys.argv[1]); solver=sys.argv[2]; seed=int(sys.argv[3]); FREE=sys.argv[4] if len(sys.argv)>4 else "0,1"
random.seed(seed)
rows=[(z,1) for z in mint]+[(z,0) for z in mis]
R=len(rows)
fa,fb=[int(t) for t in FREE.split(",")] if FREE!="none" else (None,None)
B=15 if fa is not None else 14
def base(w,z):
    if w<14: return z>>w&1
    return (z>>fa&1)|(z>>fb&1)
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
    # w0 < w1
    for x in range(W):
        for y in range(0,x+1): cl.append([-s0[j][x],-s1[j][y]])
    for r,(z,tg) in enumerate(rows):
        for s,val in ((s0[j],a[j]),(s1[j],b[j])):
            for w in range(W):
                if w<B:
                    cl.append([-s[w], val[r] if base(w,z) else -val[r]])
                else:
                    cl.append([-s[w],-val[r],v[w-B][r]]); cl.append([-s[w],val[r],-v[w-B][r]])
        A,Bv,V,T=a[j][r],b[j][r],v[j][r],t[j]
        cl+= [[-A,-Bv,V],[A,Bv,-V],[-T,A,-V],[-T,Bv,-V],[T,-A,V],[T,-Bv,V]]
for r,(z,tg) in enumerate(rows):
    cl.append([v[N-1][r] if tg else -v[N-1][r]])
# every non-output gate is used by a later gate
for j in range(N-1):
    cl.append([s0[k][B+j] for k in range(j+1,N)]+[s1[k][B+j] for k in range(j+1,N)])
if len(sys.argv)>5 and sys.argv[5]=="sb":
    for j in range(N-1):
        W=B+j
        for x in range(W):
            for y in range(x):
                cl.append([-s1[j][x],-s1[j+1][y],s0[j+1][W],s1[j+1][W]])
random.shuffle(cl)
S=Solver(name=solver,bootstrap_with=cl)
t0=time.time()
res=S.solve()
print("N",N,solver,seed,"->",res,"%.1fs"%(time.time()-t0),flush=True)
if res:
    m=set(x for x in S.get_model() if x>0)
    gates=[]
    for j in range(N):
        w0=[w for w in range(B+j) if s0[j][w] in m][0]; w1=[w for w in range(B+j) if s1[j][w] in m][0]
        gates.append(("and" if t[j] in m else "or",w0,w1))
    json.dump(gates,open("sol_%d_%s_%d.json"%(N,solver,seed),"w"))
    print(gates,flush=True)
