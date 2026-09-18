from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import io,json
OUT=Path('ML/DLSys'); DATA=Path('output/cmu-lecture-6'); BG='#F7F1E5'; INK='#302E2A'; COLORS=['#9B493A','#35647B','#536B44']
OUT.mkdir(parents=True, exist_ok=True); DATA.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':13,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':INK,'axes.facecolor':BG,'figure.facecolor':BG,'savefig.facecolor':BG,'svg.fonttype':'none'})
def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=130);fig.savefig(OUT/(name+'.svg'))
def frame(fig):
 b=io.BytesIO();fig.savefig(b,format='png',dpi=100);b.seek(0);return Image.open(b).convert('RGB')
paths=[]
for method in range(3):
 x=np.array([4.,1.5]);m=np.zeros(2);v=np.zeros(2);p=[x.copy()]
 for t in range(1,51):
  g=x*np.array([1.,20.])
  if method==0:x=x-.08*g
  elif method==1:m=.8*m+.2*g;x=x-.08*m
  else:
   m=.9*m+.1*g;v=.99*v+.01*g*g;x=x-.16*(m/(1-.9**t))/(np.sqrt(v/(1-.99**t))+1e-8)
  p.append(x.copy())
 paths.append(np.array(p))
np.savez(DATA/'optimizer-data.npz',gd=paths[0],momentum=paths[1],adam=paths[2])
fig,axs=plt.subplots(1,3,figsize=(14,8));fig.subplots_adjust(left=.065,right=.97,bottom=.36,top=.76,wspace=.30)
fig.suptitle('A gradient is not yet an update rule',fontsize=25,y=.95)
fig.text(.5,.88,r'Constructed example: $f(x,y)=\frac{1}{2}(x^2+20y^2)$ · same start (4, 1.5)',ha='center',fontsize=16)
lines=[];dots=[]
names=['Gradient descent','Momentum (EMA)','Adam (bias-corrected)']
for i,ax in enumerate(axs):
 xx,yy=np.meshgrid(np.linspace(-1,4.5,160),np.linspace(-1.8,1.8,160));ax.contour(xx,yy,.5*(xx*xx+20*yy*yy),levels=[.2,1,3,8,16,32],colors='#B6AA94',linewidths=.7)
 ax.set(xlim=(-1,4.5),ylim=(-1.8,1.8),xlabel='x (gentle curvature)',ylabel='y (steep curvature)',title=names[i]);ax.plot(0,0,'k*',ms=11);ax.plot(4,1.5,marker='s',mfc=BG,mec=INK,ms=7)
 l,=ax.plot([],[],color=COLORS[i],lw=2,marker=['o','s','^'][i],ms=3);d,=ax.plot([],[],marker=['o','s','^'][i],color=COLORS[i],ms=9);lines.append(l);dots.append(d)
fig.text(.065,.21,'Current gradient\nα = 0.08',fontsize=15)
fig.text(.39,.21,'Average past gradients\nα = 0.08, β = 0.8',fontsize=15)
fig.text(.715,.21,'Average + coordinate scaling\nα = 0.16, β₁ = 0.9, β₂ = 0.99',fontsize=15)
status=fig.text(.5,.125,'',ha='center',fontsize=16)
fig.text(.5,.055,'Exact deterministic updates, not a neural-network benchmark. Iterations ≠ wall-clock time.\nDifferent learning rates are disclosed; this illustrates mechanisms, not an optimizer ranking.',ha='center',fontsize=12)
frames=[]
for k in range(51):
 for i,p in enumerate(paths):lines[i].set_data(p[:k+1,0],p[:k+1,1]);dots[i].set_data([p[k,0]],[p[k,1]])
 status.set_text(f'Step {k:02d} / 50   ·   loss: '+ '  |  '.join(f'{names[i].split(" (")[0]} {(.5*(p[k,0]**2+20*p[k,1]**2)):.3f}' for i,p in enumerate(paths)))
 frames.append(frame(fig))
 if k==20:save(fig,'cmu-dlsys-6-optimizer-paths')
frames[0].save(OUT/'cmu-dlsys-6-optimizer-paths.gif',save_all=True,append_images=frames[1:],duration=[1500]+[180]*49+[2500],loop=0)
plt.close(fig)
# Moment propagation: analytic recurrence, explicitly not measured activations.
fig,ax=plt.subplots(figsize=(14,8));fig.subplots_adjust(left=.10,right=.69,top=.78,bottom=.21)
fig.suptitle('Initialization is a multiplier repeated at every layer',fontsize=23,y=.95)
fig.text(.5,.875,r'ReLU model: $q_{\ell+1}\approx\frac{n\sigma_w^2}{2}q_\ell$, where $q_\ell=E[z_\ell^2]$ and $q_0=1$',ha='center',fontsize=18)
ax.set(xlim=(0,30),ylim=(1e-10,1e6),yscale='log',xlabel=r'Layer depth $\ell$',ylabel=r'Activation second moment $q_\ell$ (log₁₀ scale)');ax.grid(alpha=.18)
ls=[];data=[]
for i,(fac,label) in enumerate(zip([.5,1,1.5],['σ² = 1/n → ×0.5','σ² = 2/n → ×1.0','σ² = 3/n → ×1.5'])):
 l,=ax.plot([],[],color=COLORS[i],linestyle=['--','-','-.'][i],marker=['o','s','^'][i],markevery=5,lw=2.5,label=label);ls.append(l);data.append(fac**np.arange(31))
ax.legend(loc='lower left',fontsize=13)
fig.text(.73,.69,'After 30 layers',fontsize=18)
fig.text(.73,.52,'1/n: 9.31 × 10⁻¹⁰\n\n2/n: 1\n\n3/n: 1.92 × 10⁵',fontsize=17)
fig.text(.73,.26,'Kaiming normal:\nstd = √(2 / fan_in)\n\nSecond moment is\nnot centered variance.',fontsize=14)
st=fig.text(.5,.12,'',ha='center',fontsize=16)
fig.text(.5,.055,'Theoretical recurrence, not the lecture’s MNIST measurements. Zero biases; independent zero-mean weights;\nsymmetric preactivations and a wide-layer approximation. No claim that all networks preserve scale exactly.',ha='center',fontsize=11)
ims=[]
for k in range(31):
 for l,d in zip(ls,data):l.set_data(np.arange(k+1),d[:k+1])
 st.set_text(f'Layer {k:02d} / 30 · a constant factor compounds with depth');ims.append(frame(fig))
save(fig,'cmu-dlsys-6-initialization');ims[0].save(OUT/'cmu-dlsys-6-initialization.gif',save_all=True,append_images=ims[1:],duration=[1500]+[250]*29+[2500],loop=0);plt.close(fig)
# Broadcast worked example
fig=plt.figure(figsize=(14,8));fig.suptitle('Broadcast forward; sum backward',fontsize=27,y=.94)
fig.text(.5,.855,'One shared bias affects every example in the batch.',ha='center',fontsize=17)
ax=fig.add_axes([.04,.16,.92,.61]);ax.axis('off')
blocks=[(.02,'Affine layer','Z: 2 × 3\nW: 3 × 2\nb: 2',COLORS[0]),(.35,'Forward: broadcast','ZW = [[1, 2], [3, 4]]\nb = [10, 20]\nA = [[11, 22], [13, 24]]',COLORS[1]),(.70,'Backward: reduce','∂L/∂A = [[1, 2], [3, 4]]\n∂L/∂b = [1+3, 2+4]\n             = [4, 6]',COLORS[2])]
for x,title,body,c in blocks:
 ax.text(x,.86,title,fontsize=19,color=c,weight='bold');ax.text(x,.67,body,fontsize=16,linespacing=2.1,va='top')
ax.annotate('',xy=(.32,.57),xytext=(.22,.57),arrowprops={'arrowstyle':'->','color':INK,'lw':2})
fig.text(.5,.21,r'$A=ZW+\mathbf{1}b^T \qquad \nabla_W L=Z^TG \qquad \nabla_Z L=GW^T \qquad \nabla_b L=G^T\mathbf{1}$',ha='center',fontsize=21)
fig.text(.5,.075,'Constructed local derivative example: G = ∂L/∂A already includes any activation or loss scaling.\nThe bias is logically reused across rows; broadcasting need not materialize a repeated bias matrix.',ha='center',fontsize=12)
save(fig,'cmu-dlsys-6-broadcast');plt.close(fig)
# Cover pad; preserve full content for platform crop.
p=Image.open(OUT/'cmu-dlsys-6-optimizer-paths.png').convert('RGB');c=Image.new('RGB',(round(p.height*2.5),p.height),BG);c.paste(p,((c.width-p.width)//2,0));c.save(DATA/'article-cover.png')
# checks
assert np.allclose(paths[0][1],[3.68,-.9]); assert np.all(np.isfinite(paths));assert np.allclose(data[1],1)
print('Generated 2 GIFs + 3 PNG/SVG figures; checked GD first step and moment recurrence.')
