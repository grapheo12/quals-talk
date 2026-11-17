from pathlib import Path
from lxml import etree as E
import json
R=Path(__file__).resolve().parent
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
tree=E.parse(str(R/'editable-deck.svg'));root=tree.getroot()
def el(parent,tag,**attrs):return E.SubElement(parent,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';teal='#169C9A'
wrapper=E.Element('{'+S+'}g',visibility='hidden');container=el(wrapper,'g',id='container-cloud-opening');slide=el(container,'g',id='slide-cloud-opening',**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
page=el(slide,'g',**{'class':'Page'});page.set('{'+O+'}name','Applications are moving to the cloud')
g=el(page,'g',transform='scale(26.45859375)')
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
def txt(x,y,t,size=24,color=ink,weight=400,anchor='start',parent=g):
 e=el(parent,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=t;return e
def path(d,color=blue,width=3,fill='none',parent=g):return el(parent,'path',d=d,stroke=color,stroke_width=width,fill=fill)
def rect(x,y,w,h,stroke=blue,fill='white',radius=0,parent=g):return el(parent,'rect',x=x,y=y,width=w,height=h,rx=radius,fill=fill,stroke=stroke,stroke_width=2.5)
txt(98,119,'Applications are moving to the cloud',48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
txt(115,236,'More applications',26,weight=500)
for y,label,color in [(295,'Services',blue),(380,'Analytics',blue),(465,'LLM-powered apps',teal)]:
 rect(115,y-36,58,46,color,radius=3)
 path(f'M115 {y-24}H173',color,1.8)
 for cx in [122,128,134]:el(g,'circle',cx=cx,cy=y-30,r=1.5,fill=color,stroke='none')
 if label=='Services':
  path(f'M133 {y-13}l-7 7 7 7 M154 {y-13}l7 7-7 7 M146 {y-15}l-5 19',color,2)
 elif label=='Analytics':
  for x,ht in [(128,9),(140,17),(152,23)]:el(g,'rect',x=x,y=y+4-ht,width=6,height=ht,fill=color,stroke='none')
 else:
  path(f'M128 {y-14}h29v16h-15l-6 6v-6h-8z',color,1.8)
 txt(191,y-4,label,25,color,500 if color==teal else 400)
path('M434 289H486Q502 289 502 305V359 M434 374H563 M434 459H486Q502 459 502 443V389',blue,3)
path('M549 365l16 9-16 9',blue,2.5,blue)
# A cloud boundary contains the provider's infrastructure and the vendor's model.
path('M644 501 C555 501 551 391 610 369 C572 279 658 226 734 259 C783 173 930 184 968 267 C1071 220 1159 283 1146 365 C1216 397 1189 501 1112 501 Z',blue,3.5,'#F6F8FA')
txt(872,298,'Licensed cloud services',28,blue,500,'middle')
for y in [333,360,387]:
 rect(676,y,116,23,blue,'white',3)
 el(g,'circle',cx=689,cy=y+11.5,r=3,fill=teal,stroke='none')
 path(f'M744 {y+8}h34 M744 {y+15}h34',gray,1.5)
txt(734,447,'Compute',23,ink,400,'middle')
path('M818 374H872',blue,2.5);path('M861 366l14 8-14 8',blue,2,blue)
# Neural network in a locked model container.
rect(910,323,158,92,teal,'#FFFFFF',5)
nodes=[(930,345),(930,390),(972,338),(972,369),(972,400),(1014,345),(1014,390)]
for a,b in [(0,2),(0,3),(1,3),(1,4),(2,5),(3,5),(3,6),(4,6)]:
 path(f'M{nodes[a][0]} {nodes[a][1]}L{nodes[b][0]} {nodes[b][1]}',teal,1.7)
for x,y in nodes:el(g,'circle',cx=x,cy=y,r=5,stroke=teal,stroke_width=2,fill='white')
rect(1036,365,37,32,blue,'white',3)
path('M1043 365v-9a11 11 0 0 1 22 0v9',blue,3)
el(g,'circle',cx=1054.5,cy=379,r=3,fill=blue,stroke='none');path('M1054.5 380v7',blue,2)
txt(991,447,'Proprietary LLMs',23,ink,500,'middle')
txt(991,475,'Model vendor IP',18,gray,400,'middle')
# Familiar outlined benefit callouts, matching the source deck's pill idiom.
rect(607,559,257,85,teal,'white',42)
txt(735.5,611,'Massive scale',26,teal,500,'middle')
rect(891,559,299,85,teal,'white',42)
txt(1040.5,596,'Less hardware',24,teal,500,'middle')
txt(1040.5,625,'management',24,teal,500,'middle')
txt(1182,692,'1',14.67,gray,400,'end')

meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for m in meta:
 if m.get('id','').startswith('ooo:meta_slide_'):
  n=int(m.get('id').rsplit('_',1)[1])
  if n>=1:m.set('id',f'ooo:meta_slide_{n+1}')
m=E.Element('{'+S+'}g',id='ooo:meta_slide_1')
for k,v in {'slide':'slide-cloud-opening','master':'id103','display-name':'Applications are moving to the cloud','master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
meta.insert(2,m);meta.set('{'+O+'}number-of-slides','101')
root.xpath('//*[@class="SlideGroup"]')[0].insert(1,wrapper)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide','slide-cloud-opening');idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(1,idx)
tree.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text());script="More and more applications are moving to the cloud. It allows massive scale with less hardware management overheads. In today's world, we rely more and more on LLMs. These models are private IP of the model vendors and they can only be accessed via licensed clouds."
manifest.insert(1,{'number':2,'section':'Opening','title':'Applications are moving to the cloud','text':'Applications Services Analytics LLM-powered apps Licensed cloud services Compute Proprietary LLMs Model vendor IP Massive scale Less hardware management','notes':script})
for i,s in enumerate(manifest):s['number']=i+1
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
p=R/'viewer.html';p.write_text(p.read_text().replace('max="100"','max="101"'))
print('Inserted new opening slide after the title; 101 slides total.')
