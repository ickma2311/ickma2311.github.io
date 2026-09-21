"""Reproduce teaching diagrams; no measured AlphaProof trajectories or timings.
Run: uv run --with matplotlib --with pillow python create_figures.py
Sources: Thomas Hubert, Berkeley March 2025, slides 14–21, 78–91.
"""
from pathlib import Path
import io,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
OUT=Path(__file__).parent
BG='#F7F1E5'; INK='#302E2A'; BLUE='#355F79'; SAGE='#526746'; RED='#9B4938'; OCHRE='#826321'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':16,'text.color':INK,'svg.fonttype':'none'})
def base(title,sub):
 f,a=plt.subplots(figsize=(16,9),dpi=100);f.patch.set_facecolor(BG);a.set_facecolor(BG);a.set(xlim=(0,16),ylim=(0,9));a.axis('off');f.subplots_adjust(left=0,right=1,bottom=0,top=1)
 a.text(.65,8.35,title,fontsize=30,weight='bold');a.text(.65,7.85,sub,fontsize=16,color=BLUE)
 return f,a
def box(a,x,y,w,h,title,body,c=BLUE):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.12',facecolor='#FFFCF6',edgecolor=c,linewidth=2))
 a.text(x+.22,y+h-.42,title,fontsize=19,weight='bold',color=c,va='top');a.text(x+.22,y+h-.95,body,fontsize=17,va='top',linespacing=1.6)
def arrow(a,start,end,c=BLUE):a.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'-|>','color':c,'lw':2.4,'mutation_scale':18})
def export(f,name):
 f.savefig(OUT/f'{name}.png',facecolor=BG);f.savefig(OUT/f'{name}.svg',facecolor=BG)
def raster(f):
 b=io.BytesIO();f.savefig(b,format='png',facecolor=BG);b.seek(0);return Image.open(b).convert('RGB')
frames=[]
steps=['1. State the goal','2. Propose a tempting witness','3. Check the proposal','4. Choose a prime factor instead','5. Close the obligations','VERIFIED RESULT → TRAINING EXPERIENCE']
for k in range(6):
 f,a=base('A plausible step is not a proof','Berkeley Agents · Lecture 8 · AlphaProof | Constructed arithmetic illustration')
 box(a,.65,5.25,6.5,2.1,'GOAL: find a prime greater than 5','Choose p such that p > 5 and Prime(p).\nEuclid construction: N = 5! + 1 = 121')
 box(a,9,5.25,6.25,2.1,'POLICY + SEARCH','Propose candidate steps.\nLean supplies proof-state feedback.')
 arrow(a,(7.2,6.3),(8.9,6.3))
 if k>=1:box(a,.65,2.45,4.5,2.1,'TRY p = 121','121 > 5 is true.\nIs 121 prime?',OCHRE)
 if k>=2:
  box(a,5.65,2.45,4.5,2.1,'REJECT THIS CLAIM','121 = 11 × 11\nA failed branch is not a disproof\nof the original theorem.',RED);arrow(a,(5.18,3.5),(5.6,3.5),RED)
 if k>=3:
  box(a,10.65,2.45,4.6,2.1,'TRY p = 11','11 divides 121.\n11 is prime and 11 > 5.',SAGE);arrow(a,(10.18,3.5),(10.6,3.5),SAGE)
 a.text(.75,1.58,steps[k],fontsize=24,weight='bold',color=SAGE if k>=4 else BLUE)
 a.text(.75,.99,'All proof obligations must close before the result counts as a verified proof.' if k>=4 else 'A verifier checks a proposed path; search still has to find a path that works.',fontsize=19)
 a.text(.75,.4,'Illustrative sequence, not an AlphaProof execution trace. Arithmetic checked in generation code.',fontsize=13)
 frames.append(raster(f))
 if k==5:export(f,'proof-search')
 plt.close(f)
frames[0].save(OUT/'proof-search.gif',save_all=True,append_images=frames[1:],duration=[2100,2000,2300,2100,2300,3000],loop=0)
f,a=base('Where the training signal comes from','Two models, different jobs · Lecture slides 78–85')
box(a,.65,4.85,4.45,2.45,'1  FORMALIZE STATEMENTS','Informal problem\n        ↓ formalizer\nLean statement',OCHRE)
box(a,5.8,4.85,4.45,2.45,'2  LEARN A PRIOR','Mathlib proof states\n        ↓ supervision\nProposed Lean tactics',BLUE)
box(a,10.95,4.85,4.4,2.45,'3  SEARCH + VERIFY','Try tactics in Lean\n        ↓ close all goals\nChecked proof',SAGE)
arrow(a,(10.3,6),(10.85,6))
a.text(5.35,6,'+',fontsize=26,color=BLUE)
a.text(.8,4.3,'Formal statements define the search tasks; Mathlib supervision initializes the prover.',fontsize=16)
box(a,.65,1.55,6.6,2.4,'TWO DIFFERENT CHECKS','Does Lean accept the formal proof?\nDoes the statement match the intended problem?\nThe first does not guarantee the second.',RED)
box(a,8.2,1.55,7.15,2.4,'4  REINFORCE THE PROVER','Use verified search experience for RL.\nBetter proposals guide later searches.\nThe verifier is not the learned policy.',SAGE)
arrow(a,(13.2,4.75),(13.2,4.05),SAGE)
a.text(.75,.65,'AlphaProof uses pretrained models and Mathlib supervision; it is not trained from a blank slate.',fontsize=18)
export(f,'learning-loop');plt.close(f)
frames=[]
for k in range(4):
 f,a=base('Test-time search ≠ test-time learning','Fixed weights explore more paths; test-time RL changes the prover checkpoint.')
 box(a,.65,4.75,6.6,2.45,'SEARCH ONLY','Generalist checkpoint θ\nTry more tactic sequences on the target.\nθ stays fixed during this search.',BLUE)
 box(a,8.2,4.75,7.15,2.45,'TEST-TIME RL','Start from the generalist checkpoint θ.\nGenerate related problem variants.\nUse verified successes to train.',SAGE)
 labels=[('TARGET','Hard theorem remains unresolved.'),('VARIANTS','Search related formal problems.'),('CHECKED PROOFS','Use successful proofs for weight updates.'),('SPECIALIST θ′','Retry the target with adapted weights.')]
 for j in range(k+1):
  x=.65+j*3.85;box(a,x,1.6,3.25,2.1,labels[j][0],labels[j][1].replace(' remains','\nremains').replace(' formal','\nformal').replace(' for weight','\nfor weight').replace(' adapted','\nadapted'),SAGE if j==3 else BLUE)
  if j:arrow(a,(x-.57,2.7),(x-.06,2.7),SAGE)
 a.text(.75,.68,'Conceptual sequence from slides 85–91. No measured learning curve or guarantee of solving the target.',fontsize=16)
 frames.append(raster(f))
 if k==3:export(f,'test-time-rl')
 plt.close(f)
frames[0].save(OUT/'test-time-rl.gif',save_all=True,append_images=frames[1:],duration=[2400,2400,2800,3500],loop=0)
assert math.factorial(5)+1==121==11*11
assert all(11%d for d in range(2,math.isqrt(11)+1))
def luminance(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c];return sum(x*y for x,y in zip(c,[.2126,.7152,.0722]))
contrast={c:(luminance(BG)+.05)/(luminance(c)+.05) for c in [INK,BLUE,SAGE,RED,OCHRE]}
assert min(contrast.values())>=4.5
manifest={'source':'https://rdi.berkeley.edu/adv-llm-agents/slides/alphaproof.pdf','type':'constructed teaching diagrams; not measured runs','head':'proof-search.gif','poster':'proof-search.png','contrast_on_cream':contrast,'matplotlib':matplotlib.__version__,'randomness':'none','arithmetic':'5!+1=121=11^2;11 prime;11>5','outputs':{}}
for p in OUT.glob('*'):
 if p.suffix in ['.png','.gif']:
  im=Image.open(p);manifest['outputs'][p.name]={'size':im.size,'frames':getattr(im,'n_frames',1),'bytes':p.stat().st_size}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
