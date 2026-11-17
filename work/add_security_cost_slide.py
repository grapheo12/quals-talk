from pathlib import Path
from lxml import etree as E
import json, shutil
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
sid='slide-security-cost'
assert not root.xpath(f'//*[@id="{sid}"]')
b=R/'revisions'/'before-security-cost-slide';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
blue='#1F5F8B';teal='#169C9A';ink='#1F2328';gray='#6B7785';purple='#A02B93'
w=E.Element('{'+S+'}g',visibility='hidden');c=el(w,'g',id='container-security-cost');sl=el(c,'g',id=sid,**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
p=el(sl,'g',**{'class':'Page'});title='Stronger integrity comes at a cost';p.set('{'+O+'}name',title)
g=el(p,'g',transform='scale(26.45859375)')
def txt(x,y,text,size=24,color=ink,weight=400,anchor='start',**attrs):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none',**attrs);e.text=text;return e
def path(d,color=blue,width=2.5,fill='none',**attrs):return el(g,'path',d=d,stroke=color,stroke_width=width,fill=fill,**attrs)
def dot(x,y,color):
 el(g,'circle',cx=x,cy=y,r=14,fill='white',stroke=color,stroke_width=3)
 el(g,'circle',cx=x,cy=y,r=8,fill=color,stroke='none')
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
txt(98,119,title,48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
# Ordinal scatterplot: intentionally no numeric ticks or invented measurements.
path('M260 211v369h899',blue,3)
path('M250 225l10-15 10 15 M1144 570l16 10-16 10',blue,3)
txt(135,405,'Cost',28,blue,500,'middle',transform='rotate(-90 135 405)')
txt(172,405,'(Monetary / Performance Overhead)',18,gray,anchor='middle',transform='rotate(-90 172 405)')
txt(710,625,'Security',28,blue,500,'middle')
txt(710,653,'Coverage of the threat model',20,gray,anchor='middle')
txt(278,608,'Lower',16,gray)
txt(1140,608,'Higher',16,gray,anchor='end')
txt(243,571,'Lower',16,gray,anchor='end')
txt(243,232,'Higher',16,gray,anchor='end')
# Limited-scope mechanisms at the inexpensive end.
dot(340,521,teal)
txt(370,521,'Secure boot',27,teal,500)
txt(370,548,'OS integrity at boot',20,gray)
dot(480,427,teal)
txt(510,423,'dm-verity',27,teal,500)
txt(510,450,'Read-only storage integrity',20,gray)
# Broad execution and storage protection has replication cost.
dot(920,270,purple)
txt(727,205,'Byzantine agreement',28,purple,500)
txt(727,236,'Execution + persistent storage',21,gray)
path('M938 270h44',purple,2)
for x in [994,1051,1108]:
 el(g,'rect',x=x,y=252,width=42,height=62,rx=4,fill='#F9EDF7',stroke=purple,stroke_width=2)
 for y in [265,280,295]:
  path(f'M{x+8} {y}h18',purple,1.7)
  el(g,'circle',cx=x+32,cy=y,r=2,fill=purple)
txt(1072,344,'Multiple compute',18,gray,anchor='middle')
txt(1072,368,'replicas',18,gray,anchor='middle')
txt(98,692,'Qualitative comparison',14,gray)
txt(1182,692,'4',14.67,gray,anchor='end')
manifest=json.loads((R/'deck.json').read_text());insert_at=4;count=len(manifest)+1
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for m in meta:
 if m.get('id','').startswith('ooo:meta_slide_'):
  n=int(m.get('id').rsplit('_',1)[1])
  if n>=insert_at:m.set('id',f'ooo:meta_slide_{n+1}')
m=E.Element('{'+S+'}g',id=f'ooo:meta_slide_{insert_at}')
for k,v in {'slide':sid,'master':'id103','display-name':title,'master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
meta.insert(insert_at+1,m);meta.set('{'+O+'}number-of-slides',str(count))
root.xpath('//*[@class="SlideGroup"]')[0].insert(insert_at,w)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide',sid);idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(insert_at,idx)
script='''People have been actively looking at this problem for decades and there have been a lot of security measures proposed over the years that address parts of the problem. If we look at these solutions, a clear trend emerges: the higher the amount of security measures the costlier it is. <The slide to have a scatterplot. X-axis: Security, Y-axis: Cost (Monetary/Performance Overhead)>

On one hand, secure boot guarantees your OS has not been tampered with, dm-verity checks the integrity of read-only devices. These are cheaper solutions but do not account for the full threat model. On the other hand, we have heavyweight mechanisms like Byzantine agreement. Integrity violations in both execution and persistent storage could be protected if there are all compute decisions are taken by an Byzantine agreement system and the storage layer is realized with a BFT consensus protocol. But this massively blows up the cost since now there needs to be multiple replicas of the same compute server.'''
manifest.insert(insert_at,{'number':insert_at+1,'section':'Opening','title':title,'text':' '.join(p.itertext()),'notes':script})
for i,row in enumerate(manifest):row['number']=i+1
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
v=R/'viewer.html';v.write_text(v.read_text().replace(f'max="{count-1}"',f'max="{count}"'))
c=R/'continuity.md';c.write_text(c.read_text()+'\n- Added user Slide 4 (viewer slide 5), SVG slide-security-cost: qualitative security/cost scatterplot with secure boot, dm-verity and Byzantine agreement, plus compute replicas. No numeric measurements implied; source script preserved. 104 slides total.\n')
print(f'Inserted {sid}; {count} slides')
