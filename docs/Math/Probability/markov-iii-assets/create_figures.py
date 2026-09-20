"""Exact model illustrations, MIT 6.041 L18. No sampled or empirical data."""
from pathlib import Path
import csv, json, io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from PIL import Image
import imageio_ffmpeg
import subprocess
OUT=Path(__file__).parent
BG='#F7F2E8'; INK='#283A40'; BLUE='#3C657C'; RED='#9B513C'; GREEN='#466A50'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':INK,'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})
def erlang(b,a=90):
    e=1.
    for n in range(1,b+1): e=a*e/(n+a*e)
    return e
def pmf(b):
    w=np.ones(b+1)
    for n in range(1,b+1): w[n]=w[n-1]*90/n
    return w/w.sum()
def base(title,sub):
    f=plt.figure(figsize=(16,9),dpi=100)
    f.text(.06,.94,title,size=27,weight='bold');f.text(.06,.89,sub,size=16)
    f.text(.06,.035,'MIT 6.041 · Lecture 18 | Exact model calculations · Chao Ma',size=12)
    return f
def head(b):
    f=base('Average load is not enough capacity','30 calls/min × 3 min/call = 90 Erlangs offered load · No waiting room')
    l=f.add_axes([.08,.29,.4,.48]);r=f.add_axes([.58,.29,.36,.48])
    p=pmf(b);l.bar(np.arange(b+1),p,color=BLUE,width=.9);l.bar(b,p[-1],color=RED)
    l.set(xlim=(45,117),ylim=(0,.09),xlabel='Busy lines i',ylabel='Steady-state probability')
    l.set_title(f'{b} total lines · full state highlighted',fontsize=17)
    bs=np.arange(90,116);r.plot(bs,[100*erlang(x) for x in bs],color=BLUE,lw=3)
    r.axhline(1,color=RED,ls='--',lw=2);r.text(91,1.4,'1% blocking target',size=13,color=RED)
    r.scatter([b],[100*erlang(b)],s=130,color=RED,zorder=3)
    r.set(xlim=(89,116),ylim=(0,9),xlabel='Total lines B',ylabel='Blocked arrivals (%)')
    f.text(.08,.17,f'B = {b} lines → {100*erlang(b):.3f}% blocked',size=24,weight='bold',color=RED)
    f.text(.08,.10,r'$\lambda\pi_{i-1}=i\mu\pi_i$     →     $\pi_i\propto 90^i/i!$     →     blocking = $\pi_B$',size=21)
    f.text(.58,.80,'Each frame changes capacity—not time.',size=13)
    return f
frames=[]
for b in [90,94,98,102,106,107,110,107]:
    f=head(b);buf=io.BytesIO();f.savefig(buf,format='png');frames.append(Image.open(buf).convert('RGB'))
    if b==107:f.savefig(OUT/'capacity.png');f.savefig(OUT/'capacity.svg')
    plt.close(f)
frames[0].save(OUT/'capacity.gif',save_all=True,append_images=frames[1:],duration=[1400]*8,loop=0)
writer=imageio_ffmpeg.write_frames(str(OUT/'capacity.mp4'),(1600,900),fps=10,codec='libx264',pix_fmt_out='yuv420p',macro_block_size=1);writer.send(None)
for im in frames:
    for _ in range(14): writer.send(np.asarray(im))
writer.close()
Q=np.array([[0,.6,.4],[.8,0,0],[.5,.3,0]])
a=np.linalg.solve(np.eye(3)-Q,[0,.2,0]);t=np.linalg.solve(np.eye(3)-Q,np.ones(3))
assert np.allclose(a,[9/14,5/7,15/28]);assert erlang(106)>.01>erlang(107)
f=base('Which absorbing outcome will happen?','Same transition graph; a different boundary value changes the question.')
ax=f.add_axes([.04,.19,.53,.62]);ax.set(xlim=(-.3,3),ylim=(-.4,2.5));ax.axis('off')
pos={1:(.6,.1),2:(2,.1),3:(.6,1.45),4:(2.7,1.45),5:(.0,2.15)}
edges=[(1,2,.6,.18),(2,1,.8,.18),(1,3,.4,.18),(3,1,.5,.18),(3,2,.3,0),(2,4,.2,0),(3,5,.2,0)]
for i,j,p,rad in edges:
    x,y=pos[i];u,v=pos[j];ax.add_patch(FancyArrowPatch((x,y),(u,v),connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',mutation_scale=18,lw=2,color=BLUE,shrinkA=21,shrinkB=21))
    dx=u-x;dy=v-y;mx=(x+u)/2+rad*dy*.8;my=(y+v)/2-rad*dx*.8
    ax.text(mx,my,str(p),ha='center',va='center',size=16,bbox=dict(facecolor=BG,edgecolor='none',pad=2))
for i,(x,y) in pos.items():
    ax.add_patch(Circle((x,y),.15,facecolor=GREEN if i==4 else RED if i==5 else BLUE));ax.text(x,y,str(i),color='white',ha='center',va='center',weight='bold')
ax.text(2.3,1.8,'4: target\nabsorbing',size=14,color=GREEN);ax.text(-.15,2.42,'5: other absorbing outcome',size=14,color=RED)
f.text(.61,.75,'Probability of eventually reaching 4',size=18,weight='bold')
f.text(.61,.66,r'$a_4=1,\quad a_5=0$',size=23)
f.text(.61,.46,r'$a_1=0.6a_2+0.4a_3$'+'\n'+r'$a_2=0.8a_1+0.2$'+'\n'+r'$a_3=0.5a_1+0.3a_2$',size=21,linespacing=1.7)
f.text(.61,.25,'Start 1 → 64.3%\nStart 2 → 71.4%\nStart 3 → 53.6%',size=23,color=GREEN,linespacing=1.6)
f.text(.06,.10,'First-step analysis: average the outcome probabilities after one transition.',size=20)
f.savefig(OUT/'absorption.png');f.savefig(OUT/'absorption.svg');plt.close(f)
f=base('Already there is not the same as returning','First hitting allows time 0. First return requires at least one step.')
for x,title,color in [(.07,'FIRST HIT OF STATE 1',BLUE),(.55,'FIRST RETURN TO STATE 1',RED)]:f.text(x,.76,title,size=20,weight='bold',color=color)
f.text(.07,.62,'Starting in 1: you have arrived.',size=21)
f.text(.07,.48,r'$t_1=0$',size=37,color=BLUE)
f.text(.07,.34,r'$t_2=1+0.8t_2=5$',size=26)
f.text(.55,.62,'Starting in 1: first take a step.',size=21)
f.text(.55,.48,r'$t_1^+=1+0.5(0)+0.5(5)$',size=26)
f.text(.55,.34,r'$t_1^+=3.5=1/\pi_1$',size=31,color=RED)
f.text(.07,.18,r'$P=\left(\begin{array}{cc}0.5&0.5\\0.2&0.8\end{array}\right)$' if False else 'Transitions: 1 → 2: 0.5; 2 → 1: 0.2; self-loops: 0.5 and 0.8.',size=19)
f.text(.07,.105,'A self-loop counts as a return in one step. All times here are expected steps.',size=19)
f.savefig(OUT/'hitting-return.png');f.savefig(OUT/'hitting-return.svg');plt.close(f)
with (OUT/'capacity-data.csv').open('w') as h:
    w=csv.writer(h);w.writerow(['capacity_lines','offered_load_erlangs','blocking_probability']);w.writerows((b,90,erlang(b)) for b in range(90,116))
(OUT/'validation.json').write_text(json.dumps({'model':'M/M/B/B, lambda=30/min, mu=1/3 per min, no queue','animation':'capacity scenarios, not time evolution','min_capacity_strictly_below_1pct':next(b for b in range(1,200) if erlang(b)<.01),'absorption_probabilities':a.tolist(),'expected_steps_to_either_boundary':t.tolist(),'lecture_single_absorbing_state_expected_steps':np.linalg.solve(np.eye(3)-np.array([[0,.6,.4],[.8,0,0],[.5,.5,0]]),np.ones(3)).tolist(),'data':'exact analytic calculations, no empirical samples'},indent=2))
print('Created 3 figures plus GIF, MP4, SVG, data; mathematical checks passed.')
