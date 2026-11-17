from pathlib import Path
from lxml import etree as E
import json, shutil
R=Path(__file__).resolve().parent
backup=R/'revisions'/'before-trust-slide';backup.mkdir(exist_ok=True)
for f in ['editable-deck.svg','deck.json']:shutil.copyfile(R/f,backup/f)
S='http://www.w3.org/2000/svg';O='http://xml.openoffice.org/svg/export'
tree=E.parse(str(R/'editable-deck.svg'));root=tree.getroot()
assert not root.xpath('//*[@id="slide-cloud-trust"]')
def el(parent,tag,**attrs):return E.SubElement(parent,'{'+S+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
blue='#1F5F8B';ink='#1F2328';gray='#6B7785';teal='#169C9A';purple='#A02B93'
wrap=E.Element('{'+S+'}g',visibility='hidden');cont=el(wrap,'g',id='container-cloud-trust');sl=el(cont,'g',id='slide-cloud-trust',**{'class':'Slide','clip-path':'url(#presentation_clip_path)'})
page=el(sl,'g',**{'class':'Page'});page.set('{'+O+'}name','Can we trust the cloud provider?')
g=el(page,'g',transform='scale(26.45859375)')
el(g,'rect',x=0,y=0,width=1280,height=720,fill='white',stroke='none')
def txt(x,y,t,size=24,color=ink,weight=400,anchor='start'):
 e=el(g,'text',x=x,y=y,font_family='Rubik',font_size=size,font_weight=weight,text_anchor=anchor,fill=color,stroke='none');e.text=t;return e
def path(d,color=blue,width=2.5,fill='none'):return el(g,'path',d=d,stroke=color,stroke_width=width,fill=fill)
def rect(x,y,w,h,color=blue,fill='white',radius=0):return el(g,'rect',x=x,y=y,width=w,height=h,rx=radius,stroke=color,stroke_width=2,fill=fill)
txt(98,119,'Can we trust the cloud provider?',48,weight=700)
el(g,'rect',x=98,y=140,width=67,height=4.8,fill=blue,stroke='none')
# The provider controls every layer beneath the application's interface.
rect(98,211,595,413,blue,'#F6F8FA',16)
path('M136 258c-17 0-19-21-6-26-2-16 19-22 27-11 14-8 29 3 25 16 16 7 9 21-4 21z',blue,2.5,'white')
txt(201,252,'Cloud provider controls',27,blue,500)
rect(141,288,509,61,teal,'#EAF6F5',5)
txt(395.5,327,'Your application',28,teal,500,'middle')
rect(141,366,509,44,blue,'white',3)
txt(395.5,396,'Operating system',24,blue,400,'middle')
rect(141,422,509,44,blue,'white',3)
txt(395.5,452,'Hypervisor',24,blue,400,'middle')
for x,label in [(141,'CPU'),(272,'Memory'),(403,'Disks'),(534,'Network')]:
 rect(x,483,116,96,blue,'white',4)
 cx=x+58
 if label=='CPU':
  rect(cx-14,496,28,28,blue,'#F6F8FA',2)
  for delta in [-9,0,9]:
   path(f'M{cx+delta} 490v6 M{cx+delta} 524v6 M{cx-20} {510+delta}h6 M{cx+14} {510+delta}h6',blue,1.6)
 elif label=='Memory':
  rect(cx-26,498,52,24,blue,'white',1)
  for dx in [-17,-4,9]:rect(cx+dx,504,8,11,blue,'#EAF6F5',1)
  for dx in range(-21,24,7):path(f'M{cx+dx} 522v6',blue,1.6)
 elif label=='Disks':
  path(f'M{cx-23} 500v23c0 10 46 10 46 0v-23',blue,2,'#EAF6F5')
  el(g,'ellipse',cx=cx,cy=500,rx=23,ry=7,stroke=blue,stroke_width=2,fill='white')
  path(f'M{cx-23} 512c0 10 46 10 46 0',blue,1.5)
 else:
  path(f'M{cx} 505v10 M{cx-23} 523v-8h46v8',blue,2)
  for dx,yy in [(0,496),(-23,523),(23,523)]:rect(cx+dx-7,yy,14,9,blue,'#EAF6F5',1)
 txt(cx,560,label,20,ink,400,'middle')
txt(395.5,607,'Hardware and system software',19,gray,400,'middle')
# Three concrete questions, rather than a dense threat-model bullet list.
for y,line1,line2 in [(262,'Runs my applications','correctly?'),(399,'Snoops on','my data?'),(536,'Tampers with','my data?')]:
 rect(805,y-40,378,100,purple,'white',24)
 txt(994,y,line1,26,ink,400,'middle')
 txt(994,y+34,line2,26,purple,500,'middle')
path('M716 315h57 M759 306l15 9-15 9',gray,2)
path('M716 448h57 M759 439l15 9-15 9',gray,2)
path('M716 554h57 M759 545l15 9-15 9',gray,2)
txt(1182,692,'2',14.67,gray,400,'end')

meta=root.xpath('//*[@id="ooo:meta_slides"]')[0]
for m in meta:
 if m.get('id','').startswith('ooo:meta_slide_'):
  n=int(m.get('id').rsplit('_',1)[1])
  if n>=2:m.set('id',f'ooo:meta_slide_{n+1}')
m=E.Element('{'+S+'}g',id='ooo:meta_slide_2')
for k,v in {'slide':'slide-cloud-trust','master':'id103','display-name':'Can we trust the cloud provider?','master-objects-visibility':'hidden','background-visibility':'hidden','date-time-visibility':'hidden','footer-visibility':'hidden','has-transition':'false'}.items():m.set('{'+O+'}'+k,v)
meta.insert(3,m);meta.set('{'+O+'}number-of-slides','102')
root.xpath('//*[@class="SlideGroup"]')[0].insert(2,wrap)
idx=E.Element('{'+S+'}g');idx.set('{'+O+'}slide','slide-cloud-trust');idx.set('{'+O+'}id-list','');root.xpath('//*[@class="TextShapeIndex"]')[0].insert(2,idx)
tree.write(str(R/'editable-deck.svg'),encoding='utf-8',xml_declaration=True)
manifest=json.loads((R/'deck.json').read_text())
script='Such reliance on cloud essentially raises the question: Can we trust these cloud providers? They control all the hardware: the disks, the memory, the network, the CPU, even the OS and the hypervisor are under their control. Can I trust that they are running my applications correctly? Can I trust that they are not snooping on my data, or worse tampering with my data?'
manifest.insert(2,{'number':3,'section':'Opening','title':'Can we trust the cloud provider?','text':' '.join(page.itertext()),'notes':script})
for i,s in enumerate(manifest):s['number']=i+1
(R/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False))
p=R/'viewer.html';p.write_text(p.read_text().replace('max="101"','max="102"'))
p=R/'continuity.md';p.write_text(p.read_text()+'\n- Added user Slide 2 (viewer slide 3), SVG ID slide-cloud-trust: “Can we trust the cloud provider?” Entire platform stack (application, OS, hypervisor, CPU, memory, disks, network) paired with questions about correct execution, snooping, tampering. User script preserved in notes. 102 slides total.\n')
print('Added slide 2.')
