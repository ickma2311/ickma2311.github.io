"""Reproducible teaching diagrams, not empirical measurements. Python + Matplotlib + Pillow."""
from pathlib import Path
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
P=Path(__file__).parent
BG='#F7F1E5'; INK='#302E2A'; BLUE='#365E78'; RED='#984B38'; GREEN='#526746'; GOLD='#84621F'
rc={'font.family':'DejaVu Sans','text.color':INK,'font.size':15,'svg.fonttype':'none','figure.facecolor':BG,'axes.facecolor':BG}
def canvas(title,sub):
 f,a=plt.subplots(figsize=(16,9),dpi=100); f.subplots_adjust(0,0,1,1);a.set(xlim=(0,16),ylim=(0,9));a.axis('off');a.text(.65,8.15,title,fontsize=27,weight='bold');a.text(.65,7.65,sub,fontsize=15); return f,a
def box(a,x,y,w,h,title,body='',color=BLUE,active=True):
 a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12',facecolor='#FFFDF6',edgecolor=color if active else '#BBB5AC',linewidth=2.5 if active else 1))
 a.text(x+.16,y+h-.36,title,fontsize=17,weight='bold',color=color)
 if body:a.text(x+.16,y+h-.83,body,fontsize=14,va='top',linespacing=1.6)
def arrow(a,start,end,color=BLUE): a.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',lw=2.2,color=color,connectionstyle='arc3'))
def save(f,name):
 f.savefig(P/(name+'.png'),facecolor=BG);f.savefig(P/(name+'.svg'),facecolor=BG)
with plt.rc_context(rc):
 x=np.array([1.,2.]);W1=np.array([[1.,-1.],[.5,.5]]);W2=np.array([[1.,2.],[-1.,1.]])
 z=W1@x;r=np.maximum(z,0);F=W2@r;y=x+F;g=y;dz=(W2.T@g)*(z>0);dx=g+W1.T@dz
 assert np.allclose(y,[4,3.5]) and np.allclose(dx,[9.75,9.25])
 phases=[('1 / Forward input','Input x enters the residual block.','x = [1, 2]'),('2 / First Linear','Linear uses W₁; no bias in this constructed example.','z = W₁x = [−1, 1.5]'),('3 / ReLU','ReLU keeps the positive coordinate.','r = max(z, 0) = [0, 1.5]'),('4 / Second Linear','The residual branch returns a vector matching x.','F(x) = W₂r = [3, 1.5]'),('5 / Add the shortcut','Both paths meet at tensor addition.','y = x + F(x) = [4, 3.5]'),('6 / Backward splits','For L = ½‖y‖², the add sends g to both paths.','g = ∂L/∂y = [4, 3.5]'),('7 / Branch derivative','The inactive ReLU coordinate contributes zero.','W₁ᵀ diag(0, 1) W₂ᵀg = [5.75, 5.75]'),('8 / Accumulate at x','Autodiff adds both path contributions.','∂L/∂x = [4, 3.5] + [5.75, 5.75] = [9.75, 9.25]')]
 frames=[]
 for k,(step,desc,result) in enumerate(phases):
  f,a=canvas('A residual block needs a forward rule—not a new backward engine','CMU 10-414/714 · Lecture 7 · Module composition above, tensor differentiation below')
  a.add_patch(FancyBboxPatch((3.2,3.6),8.8,2.85,boxstyle='round,pad=0.15',fill=False,edgecolor=GREEN,linestyle='--',linewidth=2))
  a.text(3.45,6.08,'Branch Module: F(x) = W₂ ReLU(W₁x)',color=GREEN,weight='bold',fontsize=18)
  box(a,.65,4.25,2,1.45,'Input x','[1, 2]',active=True)
  box(a,3.55,4.25,2.4,1.45,'Linear W₁','[−1, 1.5]' if k>=1 else 'W₁ @ x',active=k>=1)
  box(a,6.55,4.25,2,1.45,'ReLU','[0, 1.5]' if k>=2 else 'max(z, 0)',active=k>=2)
  box(a,9.15,4.25,2.5,1.45,'Linear W₂','[3, 1.5]' if k>=3 else 'W₂ @ r',active=k>=3)
  box(a,12.6,4.25,2.6,1.45,'Add → y','[4, 3.5]' if k>=4 else 'x + F(x)',color=GREEN,active=k>=4)
  for start,end in [((2.77,4.95),(3.4,4.95)),((6.08,4.95),(6.4,4.95)),((8.69,4.95),(9,4.95)),((11.78,4.95),(12.45,4.95))]:arrow(a,start,end)
  a.plot([1.65,1.65,13.9],[5.82,7.25,7.25],color=GREEN,lw=2);arrow(a,(13.9,7.25),(13.9,5.85),GREEN);a.text(6.6,7.35,'identity shortcut',color=GREEN,fontsize=14)
  a.text(2.9,3.25,'W₁ = [[1, −1], [0.5, 0.5]]       W₂ = [[1, 2], [−1, 1]]       x, y ∈ ℝ²',fontsize=15)
  if k>=5:
   a.plot([13.8,13.8,1.65],[4.05,2.65,2.65],color=RED,lw=2);arrow(a,(1.65,2.65),(1.65,4.08),RED);a.text(6,2.28,'branch contribution: W₁ᵀ D W₂ᵀ g',color=RED,fontsize=14)
   a.plot([13.4,13.4,2.05],[5.85,6.8,6.8],color=RED,lw=2);arrow(a,(2.05,6.8),(2.05,5.85),RED);a.text(4.3,6.91,'shortcut carries g unchanged',color=RED,fontsize=14)
  box(a,.7,.75,14.5,1.25,step,desc,color=RED if k>=5 else BLUE)
  a.text(.9,.36,result,fontsize=19,weight='bold',color=RED if k>=5 else BLUE)
  f.canvas.draw();frames.append(Image.fromarray(np.asarray(f.canvas.buffer_rgba())[:,:,:3].copy()))
  if k==7:save(f,'residual-autodiff')
  if k in [0,3,5,7]:frames[-1].save(P/f'review-frame-{k}.png')
  plt.close(f)
 frames[0].save(P/'residual-autodiff.gif',save_all=True,append_images=frames[1:],duration=[1500]*7+[3500],loop=0)
 f,a=canvas('The same formula, three programming contracts','Historical lecture comparison · v₂ = exp(v₁), v₃ = v₂ + 1, v₄ = v₂v₃ · at v₁ = 0: (1, 2, 2)')
 rows=[('Caffe 1.0','Layer.forward / Layer.backward','Implement each layer’s forward and local backward.\nReuse activation buffers; execute layers in order.',BLUE),('TensorFlow 1.0','Declare graph → execute fetch','Define v₂, v₃, v₄ first; then request a value.\nFetching only v₃ need not execute v₄.',GREEN),('Eager / define-by-run','Execute operations → record graph','Values appear as operations run; Python can branch.\nIf v₄ > 0.5: v₅ = 2v₄. Here v₅ = 4.',RED)]
 for i,(name,title,body,c) in enumerate(rows):
  yy=5.65-i*2.05;box(a,.7,yy,4.2,1.6,name,title,c);box(a,5.5,yy,9.7,1.6,'What the interface lets you do',body,c);arrow(a,(5,yy+.8),(5.35,yy+.8),c)
 a.text(.75,.35,'Graph visibility creates optimization opportunities; eager execution eases debugging. Neither guarantees speed.',fontsize=15)
 save(f,'programming-contracts');plt.close(f)
 f,a=canvas('One training step crosses several distinct interfaces','The model owns parameters; autodiff computes gradients; the optimizer owns update history.')
 box(a,.65,4.6,3,2,'DataLoader','batch X: B × d\nlabels: B',BLUE)
 box(a,4.45,4.6,3,2,'Module','logits: B × C\nparameters θ',GREEN)
 box(a,8.25,4.6,3,2,'Loss','logits + labels\nmean loss: scalar',GOLD)
 box(a,12.05,4.6,3.25,2,'Autodiff','backward()\nparameter grads ∇θL',RED)
 for xx in [3.8,7.6,11.4]:arrow(a,(xx,5.6),(xx+.5,5.6))
 box(a,8.25,1.15,7.05,2.2,'Optimizer: step()','Reads θ and ∇θL; updates θ.\nMomentum / Adam state persists across batches.',RED)
 arrow(a,(13.65,4.45),(13.65,3.5),RED)
 arrow(a,(8.05,2.35),(5.95,2.35),RED);arrow(a,(5.95,2.35),(5.95,4.45),RED)
 a.text(.75,3.75,'Example: B = 32 · d = 64 · C = 10',fontsize=17)
 a.text(.75,3.12,'Initialize θ once.\nClear old gradients before each\nordinary independent batch.\nKeep optimizer state across steps.',fontsize=16,linespacing=1.7,va='top')
 a.text(.75,.45,'Changing SGD to Adam does not require rewriting the model’s forward function.',fontsize=18,weight='bold')
 save(f,'training-state');plt.close(f)
manifest={'kind':'constructed exact teaching examples; no empirical benchmark','source':'https://dlsyscourse.org/slides/7-nn-framework.pdf','residual':{'x':x.tolist(),'W1':W1.tolist(),'W2':W2.tolist(),'y':y.tolist(),'loss':float(.5*y@y),'input_gradient':dx.tolist()},'versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__},'dimensions':[1600,900],'gif_duration_ms':14000,'palette':{'background':BG,'ink':INK,'blue':BLUE,'terracotta':RED,'sage':GREEN,'ochre':GOLD}}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
