import numpy as np, json, math
rng=np.random.default_rng(7)
def fps(X,n):
  idx=[int(np.argmin(X[:,1]))]; d=np.linalg.norm(X-X[idx[0]],axis=1)
  for _ in range(n-1): i=int(np.argmax(d)); idx.append(i); d=np.minimum(d,np.linalg.norm(X-X[i],axis=1))
  return X[idx]
# BRAIN: CC0 "Brain and Skull" by Drummyfish (OpenGameArt), object 'brain'
o=None; V=[]
for l in open('head.obj'):
  if l.startswith('o '): o=l.split()[1]
  elif l.startswith('v ') and o=='brain': V.append(list(map(float,l.split()[1:4])))
X=np.array(V); X[:,0]-=X[:,0].mean(); lo=X[:,1].min(); X[:,1]-=lo; X[:,2]-=X[:,2].mean()
s=62/(X[:,1].max()); X*=s; X[:,1]-=34  # ~62 units tall, centred near the default map
stem=X[X[:,1]<X[:,1].min()+3].mean(0)
B=fps(X,420)
# TREE: deterministic L-system (procedural, no license needed): trunk then 3D branching
pts=[]
def grow(p,d,L,depth):
  q=p+d*L
  for t in np.linspace(0,1,max(2,int(L/2.2))): pts.append(p+(q-p)*t)
  if depth==0: return
  k=3 if depth>2 else 2
  for i in range(k):
    a=2*math.pi*i/k+depth*1.3+rng.uniform(-.3,.3); tilt=0.55+rng.uniform(-.1,.15)
    side=np.array([math.cos(a),0,math.sin(a)]); nd=d*math.cos(tilt)+side*math.sin(tilt); nd/=np.linalg.norm(nd)
    grow(q,nd,L*0.72,depth-1)
grow(np.array([0,-46.,0]),np.array([0,1.,0]),24,5)
T=np.array(pts); T=fps(T,420)
out={'brain':np.round(B,1).tolist(),'brainStem':np.round(stem,1).tolist(),'tree':np.round(T,1).tolist()}
json.dump(out,open('anchors.json','w'),separators=(',',':'))
# DNA parameters measured from PDB 1BNA central base pairs
print(len(B),len(T),stem, len(json.dumps(out,separators=(',',':'))))
