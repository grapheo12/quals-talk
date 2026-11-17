from pathlib import Path
from lxml import etree as E
import json,shutil
R=Path(__file__).resolve().parent
b=R/'revisions'/'before-integrity-slide';b.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,b/f)
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
t=E.parse(str(R/'editable-deck.svg'));root=t.getroot()
assert not root.xpath('//*[@id="slide-integrity-scope"]')
def el(p,tag,**a):return E.SubElement(p,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in a.items()})
blue='#1F5F8B';teal='#169C9A';ink='#1F2328';gray='#6B7785'
w=E.Element('{'+S+'}g',visibility='hidden');c=el(w,'g',id='container-integrity-scope');sl=el(c,'g',id='slide-integrity-scope',**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
p=el(sl,'g',**{'class':'Page'});p.set('{'+O+'}name','This talk: Application integrity')
g=el(p,'g',transform='scale(26.45859375)')
def txt(x,y,text,size=24,color=ink,weight=400,anchor='middle'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=text;return e
def path(d,color=blue,width=3,fill='none'):return el(g,'path',d=d,stroke=color,stroke_width=width,fill=fill)
def rect(x,y,width,height,color=blue,fill='white',radius=0):return el(g,'rect',x=x,y=y,width=width,height=height,rx=radius,stroke=color,stroke_width=2.5,fill=fill)
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
txt(98,119,'This talk: Application integrity',48,weight=700,anchor='start')
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
rect(465,204,350,78,teal,'#EAF6F5',5)
txt(640,253,'Your application',30,teal,500)
path('M640 283v39 M355 357v-35h570v35',blue,2.5)
path('M347 345l8 13 8-13 M917 345l8 13 8-13',blue,2.5)
# Runtime: CPU execution and memory, paired within one integrity boundary.
rect(127,377,456,231,blue,'#F6F8FA',16)
txt(355,420,'Execution & memory',28,blue,500)
rect(222,453,66,66,blue,'white',5)
rect(238,469,34,34,teal,'#EAF6F5',2)
for d in [-21,-7,7,21]:
 path(f'M{255+d} 443v10 M{255+d} 519v10 M212 {486+d}h10 M288 {486+d}h10',blue,2)
rect(371,466,110,40,blue,'white',3)
for dx in [383,409,435]:rect(dx,475,16,20,teal,'#EAF6F5',1)
for dx in range(380,478,12):path(f'M{dx} 506v10',blue,2)
txt(255,563,'Running execution',20)
txt(426,563,'Memory',20)
# Persistent state: the same disk-cylinder vocabulary used throughout the deck.
rect(697,377,456,231,blue,'#F6F8FA',16)
txt(925,420,'Persistent storage',28,blue,500)
path('M868 458v69c0 28 114 28 114 0v-69',blue,3,'#EAF6F5')
el(g,'ellipse',cx=925,cy=458,rx=57,ry=17,fill='white',stroke=blue,stroke_width=3)
path('M868 481c0 26 114 26 114 0 M868 504c0 26 114 26 114 0',blue,2)
txt(925,580,'Persistent state',20)
txt(1182,692,'3',14.67,gray,anchor='end')
meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for m in meta:
 if m.get('id','').startswith('ooo:meta_slide_'):
  n=int(m.get('id').rsplit('_',1)[1])
  if n>=3:m.set('id',f'ooo:meta_slide_{n+1}')
m=E.Element('{'+S+'}g',id='ooo:meta_slide_3')
for k,v in {'slide':'slide-integrity-scope','master':'id103','display-name':'This talk: Application integrity','master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
meta.insert(4,m);meta.set('{'+O+'}number-of-slides','103')
root.xpath('//*[@class="SlideGroup"]')[0].insert(3,w)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide','slide-integrity-scope');idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(3,idx)
t.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text())
script='Now in this talk I am going to focus on the integrity aspect of your application. Specifically, integrity of the running execution and memory, and integrity of persistent storage.'
manifest.insert(3,{'number':4,'section':'Opening','title':'This talk: Application integrity','text':' '.join(p.itertext()),'notes':script})
for i,row in enumerate(manifest):row['number']=i+1
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
p=R/'viewer.html';p.write_text(p.read_text().replace('max="102"','max="103"'))
p=R/'continuity.md';p.write_text(p.read_text()+'\n- Added user Slide 3 (viewer slide 4), SVG slide-integrity-scope: “This talk: Application integrity”. Application branches into execution/memory (CPU and RAM icons) and persistent storage (disk cylinder). Script in notes. 103 slides total.\n')
