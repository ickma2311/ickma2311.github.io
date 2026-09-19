"""Original teaching diagrams; constructed examples, no measured model results.
Run with matplotlib, pillow, numpy, imageio-ffmpeg. Outputs beside this script.
Design workflow: scientific-visualization, Kassis et al. (2026), arXiv:2609.00065.
"""
from pathlib import Path
import io, json, subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image
import imageio_ffmpeg

OUT=Path(__file__).resolve().parent
BG='#F7F2E8'; INK='#283A40'; BLUE='#3C657C'; RED='#9B513C'; GREEN='#466A50'; PALE='#E6DFD1'
STYLE={'font.family':'DejaVu Sans','text.color':INK,'font.size':15,'svg.fonttype':'none', 'figure.facecolor':BG,'axes.facecolor':BG}
def text(ax,x,y,s,size=17,color=INK,**kw):return ax.text(x,y,s,fontsize=size,color=color,va='top',**kw)
def box(ax,x,y,w,h,fill=BG,edge=INK,lw=1.3):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.01,rounding_size=0.08',facecolor=fill,edgecolor=edge,linewidth=lw))
def arrow(ax,x,y,u,v,col=BLUE):ax.annotate('',xy=(u,v),xytext=(x,y),arrowprops={'arrowstyle':'->','color':col,'lw':2.2})
def base(title,sub):
 f,a=plt.subplots(figsize=(16,9),dpi=100);f.subplots_adjust(0,0,1,1);a.set(xlim=(0,16),ylim=(0,9));a.axis('off')
 text(a,.65,8.6,title,29,fontfamily='DejaVu Serif',weight='bold');text(a,.65,7.98,sub,15,color=BLUE)
 return f,a
def save(f,name):
 f.savefig(OUT/(name+'.png'));f.savefig(OUT/(name+'.svg'))
def raster(f):
 b=io.BytesIO();f.savefig(b,format='png');b.seek(0);return Image.open(b).convert('RGB')

def loop_frame(step):
 f,a=base('A correct click is not a completed task','Berkeley Advanced LLM Agents · Lecture 7 · Perception → action → evidence')
 text(a,.65,7.47,'GOAL  Add both receipts and save the updated ledger.',20,weight='bold')
 box(a,.65,3.1,3.05,3.8,fill='#EEE7D9');text(a,.88,6.67,'SOURCE RECEIPTS',16,color=BLUE,weight='bold')
 text(a,.9,6.1,'A   Supplies',17);text(a,.9,5.67,'$18.50',25,fontfamily='DejaVu Serif')
 text(a,.9,4.96,'B   Transit',17);text(a,.9,4.53,'$26.40',25,fontfamily='DejaVu Serif')
 text(a,.9,3.72,'Expected total: $44.90',15,weight='bold')
 box(a,4.05,3.1,6.5,3.8,fill='#FFFCF5');text(a,4.3,6.67,'ledger.xlsx'+('  • unsaved' if step in [1,2] else ''),17,weight='bold')
 a.add_patch(Rectangle((4.28,5.55),6.05,.58,facecolor=PALE,edgecolor=INK,lw=.6))
 for x,s in [(4.48,'Item'),(8.68,'Amount')]:text(a,x,5.98,s,16,weight='bold')
 vals=['18.50' if step>=1 else '—','26.40' if step>=2 else '—','44.90' if step>=2 else '—']
 for j,(s,val) in enumerate(zip(['Supplies','Transit','Total'],vals)):
  y=5.52-j*.58;a.add_patch(Rectangle((4.28,y-.54),6.05,.56,facecolor=BG if j==2 else '#FFFCF5',edgecolor=PALE,lw=.8))
  text(a,4.48,y-.06,s,17,weight='bold' if j==2 else 'normal');text(a,8.9,y-.06,val,17,weight='bold' if j==2 else 'normal')
 box(a,8.88,3.35,1.4,.46,fill=GREEN if step>=3 else BLUE,edge=GREEN if step>=3 else BLUE)
 text(a,9.58,3.73,'Saved' if step>=3 else 'Save',14,color='white',ha='center')
 if step in (1,2):
  y=5.52-(step-1)*.58;a.add_patch(Rectangle((8.5,y-.54),1.83,.56,fill=False,edgecolor=BLUE,lw=2.6))
 if step==3:arrow(a,10.8,3.72,10.18,3.59)
 labels=['Observe the current screen','Enter receipt A','Enter receipt B; recompute','Save the workbook','Check the persisted file']
 actions=['Read both receipts.\nLocate the amount cells.','type("18.50")\nObserve the changed cell.','type("26.40")\n18.50 + 26.40 = 44.90','Click Save.\nThen inspect the new state.','Read saved rows and total.\nCompare with the task goal.']
 box(a,10.94,3.1,4.4,3.8,fill='#EAEDE5' if step==4 else BG)
 text(a,11.2,6.65,f'{step+1:02d}  {labels[step]}',15,weight='bold',color=GREEN if step==4 else BLUE)
 text(a,11.2,5.86,actions[step],17,linespacing=1.7)
 text(a,11.2,4.57,'TASK EVIDENCE',14,color=BLUE,weight='bold')
 evidence=['No result yet.','One row is still missing.','Values visible ≠ file saved.','Save action ≠ verified file.','Two rows ✓   Total ✓\nSaved artifact ✓']
 text(a,11.2,4.06,evidence[step],16,color=GREEN if step==4 else RED,linespacing=1.5)
 for i,name in enumerate(['Observe','Enter A','Enter B','Save','Verify']):
  x=1.5+i*3.15;a.plot(x,2.28,'o',ms=18,color=GREEN if i<=step else PALE)
  text(a,x,1.85,name,17,ha='center',weight='bold' if i==step else 'normal')
  if i<4:arrow(a,x+.3,2.28,x+2.85,2.28,GREEN if i<step else '#81786A')
 text(a,.65,.86,'OSWorld evaluates the resulting state; it need not match one reference click sequence.',17,weight='bold')
 text(a,.65,.39,'Constructed teaching example inspired by lecture slides 11–19. Animation shows state transitions, not benchmark performance.',12)
 return f

def data_figure():
 f,a=base('Useful training data needs more than a plausible answer','Two distinct uses of synthetic actions · AgentTrek and TACO')
 text(a,.7,7.35,'AgentTrek: turn a tutorial into an executed trajectory',22,fontfamily='DejaVu Serif',weight='bold')
 cols=[.7,5.85,11.0]
 for x in cols:box(a,x,4.23,4.3,2.56)
 for x,title,body in zip(cols,['1  Structure the tutorial','2  Replay in an environment','3  Filter before training'],['Goal: export a chart as PNG\nApp version + prerequisites\nSteps + expected output','Observe: chart editor\nAction: choose PNG, export\nRecord screens and actions','Inspect trajectory + outcome\nKeep supported successes\nReject failed / poor traces']):
  text(a,x+.22,6.54,title,16,color=BLUE,weight='bold');text(a,x+.22,5.96,body,16,linespacing=1.65)
 arrow(a,5.08,5.42,5.68,5.42);arrow(a,10.23,5.42,10.83,5.42)
 text(a,.7,3.72,'TACO: use a tool to resolve a visual question',22,fontfamily='DejaVu Serif',weight='bold')
 for x in cols:box(a,x,1.02,4.3,2.14,fill='#ECEEE5')
 for x,title,body in zip(cols,['Image question','Action + observation','Answer from the result'],['Receipt: 3 items × $12.50\nQuestion: what is the total?','OCR → 3 and 12.50\nCalculator → 3 × 12.50','Total = $37.50\nTool outputs support the answer']):
  text(a,x+.22,2.92,title,16,color=GREEN,weight='bold');text(a,x+.22,2.3,body,16,linespacing=1.6)
 arrow(a,5.08,2.05,5.68,2.05,GREEN);arrow(a,10.23,2.05,10.83,2.05,GREEN)
 text(a,.7,.53,'Constructed examples. A model-based trajectory filter can still be wrong; a correct answer alone does not validate every step.',13)
 return f

def grounding_figure():
 f,a=base('Grounding answers “where”; planning answers “what next”','Aguvis connects visual observations, an intermediate instruction, and an executable action')
 # A precisely scaled 1000 x 600 teaching screen, origin top-left.
 x0,y0,w,h=.8,3.16,8.0,4.2
 a.add_patch(Rectangle((x0,y0),w,h,facecolor='#FFFCF5',edgecolor=INK,lw=1.8))
 a.add_patch(Rectangle((x0,y0+h-.48),w,.48,facecolor=PALE,edgecolor='none'))
 text(a,1.05,7.2,'Export report',15,weight='bold')
 text(a,1.1,6.43,'File name',17);box(a,3.07,5.98,4.85,.5);text(a,3.28,6.39,'report.png',15)
 text(a,1.1,5.5,'Format',17);box(a,3.07,5.03,4.85,.5);text(a,3.28,5.42,'PNG',15)
 # x=800, y=450 -> 7.2,4.21.
 cx=x0+w*.8;cy=y0+h*(1-.75)
 box(a,cx-.65,cy-.28,1.3,.56,fill=BLUE,edge=BLUE);text(a,cx,cy+.15,'Export',14,color='white',ha='center')
 a.plot([x0,cx],[cy,cy],ls='--',color=RED,lw=1.5);a.plot([cx,cx],[cy,y0+h],ls='--',color=RED,lw=1.5)
 text(a,4.4,7.66,'width = 1000 pixels',15,ha='center');text(a,1.1,3.66,'Target center = (800, 450)',16,color=RED)
 text(a,.8,2.7,'Normalized target: (u, v) = (800/1000, 450/600) = (0.8, 0.75)',18,weight='bold')
 text(a,.8,2.15,'Origin at top-left; height = 600 pixels. Convert back using the current screen size.',14)
 box(a,9.35,3.16,5.85,4.2,fill='#ECEEE5')
 text(a,9.62,7.06,'GOAL → INSTRUCTION → ACTION',16,color=GREEN,weight='bold')
 text(a,9.62,6.47,'Goal: save the report as a PNG.\n\nInstruction: confirm PNG, then click Export.\n\nAction: click the grounded target.\n\nFeedback: does report.png now exist?',17,linespacing=1.3)
 text(a,.8,1.35,'Stage 1: learn visual target locations.',18,color=BLUE,weight='bold')
 text(a,8.3,1.35,'Stage 2: learn multi-step decisions.',18,color=GREEN,weight='bold')
 text(a,.8,.77,'Changing layout can move the target. A unified action format does not make coordinates invariant.',17,weight='bold')
 text(a,.8,.32,'Constructed coordinate example; conceptual summary of lecture slides 69–82, not a trace from a trained Aguvis model.',12)
 return f

with plt.rc_context(STYLE):
 frames=[]
 for step in range(5):
  fig=loop_frame(step);frames.append(raster(fig))
  if step==4:save(fig,'berkeley-7-action-evidence')
  plt.close(fig)
 frames[0].save(OUT/'berkeley-7-action-evidence.gif',save_all=True,append_images=frames[1:],duration=[2800,2800,3400,3400,4600],loop=0,optimize=False)
 for name,fn in [('berkeley-7-training-data',data_figure),('berkeley-7-grounding',grounding_figure)]:
  fig=fn();save(fig,name);plt.close(fig)
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-i',str(OUT/'berkeley-7-action-evidence.gif'),'-vf','fps=20,format=yuv420p','-movflags','+faststart',str(OUT/'berkeley-7-action-evidence.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def luminance(h):
 rgb=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return sum(v*k for v,k in zip([v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb],[.2126,.7152,.0722]))
contrasts={c:round((luminance(BG)+.05)/(luminance(c)+.05),2) for c in [INK,BLUE,RED,GREEN]}
assert all(v>=4.5 for v in contrasts.values())
manifest={'provenance':'Original constructed examples; no empirical claims or sampled model trajectories','source':'Caiming Xiong, Berkeley lecture, 2025-03-17, slides 11–19, 35–61, 69–82','frames':5,'duration_ms':17000,'dimensions':[1600,900],'palette_contrast_vs_cream':contrasts,'software':{'matplotlib':matplotlib.__version__},'files':{p.name:p.stat().st_size for p in OUT.glob('berkeley-7-*')}}
(OUT/'figure-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
